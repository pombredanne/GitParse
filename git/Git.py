import subprocess, re, httplib, json
from gus.BacklogClient import BacklogClient
from collab.CodeCollab import CodeCollabClient

class Author:
    a_name = ''
    a_email = ''

    def __init__(self):
        author = subprocess.check_output(['git','log','-1','--pretty=format:%cn,%ce'])
        self.a_name, self.a_email = author.split(",")

    def name(self):
        return self.a_name

    def email(self):
        return self.a_email

class Comment:
    title = ''
    overview = ''

    def __init__(self):
        out = subprocess.check_output(['git', 'log', '-1', '--pretty=format:%B'])
        out = out.replace('"', '')
        commit_array = out.split("\n")
        self.title, self.overview = commit_array[0], "\n".join(commit_array[1:])

    def subject(self):
        return self.title

    def body(self):
        return self.overview
    
    def annotations(self):
        out = {}
        regex = re.compile("@([^\s]*) ([^\s]*)",re.MULTILINE)
        
        for k, v in regex.findall(self.title):
            out[k] = v
        for k, v in regex.findall(self.overview):
            out[k] = v

        return out

class Changes:
    def list(self):
        changelist = subprocess.check_output(['git', 'log', '-1', '--name-status', '--pretty=format:%cd'])
        changelist = changelist.replace('\t',': ')
        changes = changelist.split("\n")
        # removes the first line of the output so that all left is the changelist
        changeout = "\n".join(changes[1:])
        return changeout

class Patch:
    def diff(self):
        diff = subprocess.check_output(['git','log','-1','--unified=100000','--pretty=format:%cd'])
        diff_array = diff.split("\n")
        # removes the first line of the output so all that is left is the diff
        diffout = "\n".join(diff_array[1:])
        return diffout
    
class PostCommit:
    def buildCommit(self):
        '''
        Parses the last git commit log entry and creates a data structure with the relevant parts 
        ''' 
        author = Author()
        comment = Comment()
        changes = Changes()
        diff = Patch()
        
        commit = {
            'author'       : author.name(),
            'email'        : author.email(),
            'title'        : comment.subject(),
            'overview'     : comment.body(),
            'annotations'  : comment.annotations(),
            'changelist'   : changes.list(),
            'unified_diff' : diff.diff(),
        }
        
        return commit
    
    def gus(self, commit):
        '''
        Updates the gus item to fixed as long as there is a 'fixes' and 'scheduled_build'
        annotation in the commit message
        '''
        try:
            scheduled_build = commit['annotations']['scheduled_build']
            work_name = commit['annotations']['fixes']
            gus = BacklogClient()
            buildid = gus.find_build_id(scheduled_build)
            work = gus.find_work(work_name)
            gus.mark_work_fixed(work["Id"], buildid)
            gus.add_changelist_comment(work["Id"], "%s\n\n%s" % (commit['title'], commit['overview']), commit['changelist'])
            print 'Updated Work Item %s (%s) status to Fixed in build %s' % (work_name, work['Id'], scheduled_build)
        except Exception as e:
            print 'Seems to be missing Gus ID/Build or unable to reach Gus. Not updating Gus'
            print e
    
    def collab(self, commit, author=None):
        '''
        Creates a code review in code collaborator from the git logs if there is
        a 'reviewers' annotation in the commit message
        '''
        try:
            reviewers = commit['annotations']['reviewers']
            cc = CodeCollabClient()
            review_id = cc.create_collab(commit['title'], commit['overview'])
            cc.add_diffs(review_id, commit['unified_diff'])
            if author is None:
                author = cc.get_current_user()
            cc.add_reviewers(review_id, author, reviewers)
            cc.done(review_id)
            print 'Created code review %s for author %s' % (review_id, author)
        except Exception as e:
            print 'No reviewer specified for commit, can\'t create review'
            print e
        
    def commit(self):
        '''
        Builds the commit from the git logs and performs gus and code collab
        tasks directly.  Use remote if you want to post the commit to an
        async service which in turn, calls this method.
        '''
        commit = self.buildCommit()
        self.gus(commit)
        self.collab(commit)
        
    def remote(self, server='localhost:8000'):
        ''' 
        Establishes identities for GUS and Code collab for proxy ticket update
        and code review creation.  Code collab client cannot activate review for
        remote.
        '''
        gus = BacklogClient()
        session_id = gus.session_id()
        cc = CodeCollabClient()
        author = cc.get_current_user()
        commit = self.buildCommit()
        commit['gus_session'] = session_id
        commit['collab_user'] = author
        
        with httplib.HTTPConnection(server) as conn:
            head = {
                'Content-Type' : 'application/json',
                'Accept'       : 'application/json'
            }
            conn.request('POST','/service/post', json.dumps(commit), head)
            response = conn.getresponse()
            print response.status, response.reason
            data = response.read()
            conn.close()
            
            print data

        
