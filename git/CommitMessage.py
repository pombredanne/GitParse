from .Git import Comment
from gus.BacklogClient import BacklogClient

class CommitMessage:
    '''
    Use this from a the commit-msg git commit hook by calling the validate method
    
        #!/usr/bin/env python
        import sys
        from git.Git import CommitMessage
        cm = CommitMessage()
        cm.validate(sys.argv[1])
        
    '''
    def work_in_progress(self, gus_id):
        try:
            gus = BacklogClient()
            work = gus.find_work(gus_id)
            status = work['Status']
            
            valid = status == 'In Progress'
        except:
            valid = False
            
        return valid
    
    def build_valid(self, build_id):
        try:
            gus = BacklogClient()
            build = gus.find_build_id(build_id)
            valid = build is not None
        except:
            valid = False
            
        return valid
    
    def validate(self, msg_file):
        with open(msg_file) as f:
            message = f.read()
            f.close()
            
        comment = Comment(comment=message)
        annotations = comment.annotations()
        
        valid = False
        
        if 'fixes' in annotations:
            if 'scheduled_build' in annotations:
                if self.build_valid(annotations['scheduled_build']):
                    if self.work_in_progress(annotations['fixes']):
                        valid = True
                    else:
                        print "Work %s status is not In Progress, please update GUS before committing" % annotations['fixes']
                else:
                    print "Build %s is not a valid build label, please use the correct @scheduled_build" % annotations['scheduled_build']
            else:
                print "You must specify a valid build label for this fix"
        else:
            print "All commits should include a GUS work id.  Please annotation your commit with an In Progress GUS id using @fixes"
        
        return valid

