from .Git import Comment
from gus.BacklogClient import BacklogClient
from gus.Gus import NoRecordException
from collab.CodeCollab import CodeCollabClient
from ci.jenkins import MrHat
import sys

class CommitMessage:
    """
    Use this from a the commit-msg git commit hook by calling the validate method
    
        #!/usr/bin/env python
        import sys
        from git.CommitMessage import CommitMessage
        cm = CommitMessage()
        cm.validate(sys.argv[1])
        
    If you want to cherry pick your validators do the following:
    
        #!/usr/bin/env python
        import sys
        from git.CommitMessage import CommitMessage
        cm = CommitMessage(auto=False)
        cm.do_gus_check()
        cm.do_in_progress_check()
        cm.do_build_check()
        cm.validate(sys.argv[1])
        
    """
    def __init__(self, auto=True):
        print "Code Collab 6.5 command line is very slow, please wait..."
        self.validators = []
        
        if auto:
            self.do_gus_check()
            self.do_in_progress_check()
            self.do_build_check()
            #self.do_review_check()
            self.do_valid_review_check()
            
    def do_gus_check(self):
        '''
        Enables Gus Annotation validation.
        '''
        self.validators.append(GusValidator())
    
    def do_build_check(self):
        '''
        Enables Build label validation.
        '''
        self.validators.append(BuildValidator())
           
    def do_in_progress_check(self):
        '''
        Enables Work In Progress validation
        '''
        self.validators.append(InProgressValidator())
        
    def do_review_check(self):
        '''
        Enables update review validation
        '''
        self.validators.append(ReviewValidator())
        
    def do_valid_review_check(self):
        self.validators.append(ReviewInProgressValidator())

    def validate(self, msg_file):
        '''
        Validates a file containing a commit message
        '''
        with open(msg_file) as f:
            message = f.read()
            f.close()
            
        messages = []
        comment = Comment(comment=message)
        for validator in self.validators:
            vmessages = validator.validate(comment)
            for message in vmessages:
                messages.append(message)
            
        for message in messages:
            print message
            
        if len(messages) > 0:
            sys.exit(1)

class BuildValidator:
    '''
    Ensures that the message contains a valid @scheduled_build or @next
    '''
    def validate(self, comment):
        messages = []
        annotations = comment.annotations()
        build_id = None
        
        if 'scheduled_build' in annotations:
            build_id = annotations['scheduled_build']
        elif 'next' in annotations:
            mrhat = MrHat()
            build_id = mrhat.find_next_build(annotations['next'])
            
        if build_id is not None:
            try:
                gus = BacklogClient()
                gus.find_build_id(build_id)
            except NoRecordException:
                messages.append("Build label %s is not valid.  Please specify a valid build label with either @scheduled_build or @next." % build_id)
            except:
                messages.append("Unable to connect to Gus to validate build. Connect to vpn before committing")
            
        return messages
        
class InProgressValidator:
    '''
    Ensures that id's specified by the @fixes annotation represent work that is 
    currently 'In Progress'
    '''
    def validate(self, comment):
        messages = []
        annotations = comment.annotations()
        if 'fixes' in annotations:
            gus_id = annotations['fixes']
            gus = BacklogClient()
            try:
                work = gus.find_work(gus_id)
                status = work['Status__c']
                
                if status != 'In Progress':
                    messages.append("Work %s status is not In Progress, please update GUS before committing" % gus_id)
            except NoRecordException:
                messages.append("Invalid GUS id: %s.  Please use a valid W# in Gus" % gus_id)
                GusHelper().show_potential_work(messages)
            except:
                messages.append("Can't connect to GUS to check work status.  Connect to vpn before committing.")
                
        return messages

class GusHelper:
    def show_potential_work(self, messages):
        gus = BacklogClient()
        userid = gus.get_current_user_id()
        current_work = gus.get_potential_work_for_user(userid)
        
        if len(current_work) > 0:
            messages.append("Perhaps one of these:")
            for work in current_work:
                s = "\t%s (%s): %s" % (work[0], work[1], work[2])
                if s not in messages:
                    messages.append(s)    
                    
class GusValidator:
    '''
    Ensures that the commit message contains a @fixes and either @scheduled_build or @next
    value.
    '''
    def validate(self, comment):
        messages = []
        annotations = comment.annotations()
        
        if 'fixes' in annotations:
            if 'scheduled_build' not in annotations and 'next' not in annotations:
                messages.append("You must specify a valid build label for this fix using @scheduled_build or @next")
        elif 'updates' not in annotations:
            messages.append("All commits should include a GUS work id.  Please annotate your commit with an In Progress GUS id using @fixes or @updates")
            GusHelper().show_potential_work(messages)
        
        return messages

class ReviewValidator:
    def validate(self, comment):
        messages = []
        
        if 'reviewers' not in comment.annotations() and 'update_review' not in comment.annotations():
            messages.append("No review annotations specified.  You need to either create a new review with @reviewers or @update_review with id")
        
        return messages
    
class ReviewInProgressValidator:
    '''
    Ensures that any update_review annotations are referencing valid reviews
    '''
    def validate(self, comment):
        messages = []
        annotations = comment.annotations()
        
        if 'update_review' in annotations:
            cc = CodeCollabClient()
            user = cc.get_current_user()
            author = cc.get_review_author(annotations['update_review'])
            if user != author:
                messages.append("You are not the author of review %s.  Please ensure you have the correct review id for @update_review." % annotations['update_review'])
                
            status = cc.get_review_status(annotations['update_review'])
            if status == 'Completed':
                messages.append("The review specified (%s) is already Complete.  Create a new review with @reviewers" % annotations['update_review'])

        return messages