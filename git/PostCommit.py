from .Git import Author, Comment, Changes, Patch
from gus.BacklogClient import BacklogClient
from collab.CodeCollab import CodeCollabClient
from ci.jenkins import MrHat
import httplib, json

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
        if ('scheduled_build' in commit['annotations'] or 'next' in commit['annotations']) and 'fixes' in commit['annotations']:
            if 'next' in commit['annotations']:
                mrhat = MrHat()
                scheduled_build = mrhat.find_next_build(commit['annotations']['next'])
            else:
                scheduled_build = commit['annotations']['scheduled_build']
                
            work_name = commit['annotations']['fixes']
            try:
                if 'gus_session' in commit:
                    gus = BacklogClient(session_id=commit['gus_session'])
                else:
                    gus = BacklogClient()
                buildid = gus.find_build_id(scheduled_build)
                work = gus.find_work(work_name)
                gus.mark_work_fixed(work["Id"], buildid)
                gus.add_changelist_comment(work["Id"], "%s\n\n%s" % (commit['title'], commit['overview']), commit['changelist'])
                print 'Updated Work Item %s (%s) status to Fixed in build %s' % (work_name, work['Id'], scheduled_build)
            except Exception as e:
                print 'Unable to update Gus: %s' % str(e)
        else:
            print 'No Gus annotations (scheduled_build, fixed), not updating Gus'
    
    def collab(self, commit, author=None):
        '''
        Creates a code review in code collaborator from the git logs if there is
        a 'reviewers' annotation in the commit message
        '''
        if 'reviewers' in commit['annotations']:
            reviewers = commit['annotations']['reviewers']
            cc = CodeCollabClient()
            review_id = cc.create_collab(commit['title'], commit['overview'])
            cc.add_diffs(review_id, commit['unified_diff'])
            if author is None:
                author = cc.get_current_user()
            cc.add_reviewers(review_id, author, reviewers)
            cc.done(review_id)
            print 'Created code review %s for author %s' % (review_id, author)
        else:
            print 'No reviewers specified for commit, can\'t create review'
        
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
        
        conn = httplib.HTTPConnection(server)
        head = {
            'Content-Type' : 'application/json',
            'Accept'       : 'application/json'
        }
        conn.request('POST','/service/post', json.dumps(commit), head)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        
        print data
    