from .Git import Author, Comment, Changes, Patch
from gus.BacklogClient import BacklogClient
from collab.CodeCollab import CodeCollabClient
from ci.jenkins import MrHat
import httplib, json

class PostCommit:
    '''
    Processing helper for post commit in Git.  Call by implementing a new .git/hooks/post-commit
    and using:
    
        #!/usr/bin/env python
        from git.PostCommit import PostCommit
        pc = PostCommit()
        pc.commit()
        
    To utilize a web service for async processing, make your post-commit look like:
    
        #!/usr/bin/env python
        from git.PostCommit import PostCommit
        pc = PostCommit()
        pc.remote()
        
    The default service is localhost:8000, if you want to process on a remote service call
    
        pc.remote(server='remoteserver.com:8000')
    '''
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
        if self.__is_valid_fix__(commit):
            if 'next' in commit['annotations']:
                mrhat = MrHat()
                scheduled_build = mrhat.find_next_build(commit['annotations']['next'])
            else:
                scheduled_build = commit['annotations']['scheduled_build']
                
            work_name = commit['annotations']['fixes']
            
            try:
                gus = self.__gus_session__(commit)
                buildid = gus.find_build_id(scheduled_build)
                work = gus.find_work(work_name)
                gus.mark_work_fixed(work["Id"], buildid)
                gus.add_changelist_comment(work["Id"], "%s\n\n%s" % (commit['title'], commit['overview']), commit['changelist'])
                print 'Updated Work Item %s (%s) status to Fixed in build %s' % (work_name, work['Id'], scheduled_build)
            except Exception as e:
                print 'Unable to update Gus: %s' % str(e)
        elif 'updates' in commit['annotations']:
            work_name = commit['annotations']['updates']
            try:
                gus = self.__gus_session__(commit)
                work = gus.find_work(work_name)
                gus.mark_work_in_progress(work["Id"])
                gus.add_changelist_comment(work["Id"], "%s\n\n%s" % (commit['title'], commit['overview']), commit['changelist'])
                print 'Updated Work Item %s (%s) status to In Progress' % (work_name, work['Id'])
            except Exception as e:
                print 'Unable to update Gus: %s' % str(e)
        else:
            print 'No Gus annotations (scheduled_build, fixed), not updating Gus'
            
    def __is_valid_fix__(self, commit):
        if 'fixes' in commit['annotations']:
            return 'scheduled_build' in commit['annotations'] or 'next' in commit['annotations']
        else:
            return False

    def __gus_session__(self, commit):
        if 'gus_session' in commit:
            gus = BacklogClient(session_id=commit['gus_session'])
        else:
            gus = BacklogClient()
        return gus
    
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
        mrhat = MrHat()
        creds = mrhat.get_current_creds()
        commit = self.buildCommit()
        commit['gus_session'] = session_id
        commit['collab_user'] = author
        commit['jenkins_user'] = creds[0]
        commit['jenkins_token'] = creds[1]
        
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
    