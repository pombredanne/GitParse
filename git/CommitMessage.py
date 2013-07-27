from .Git import Comment
from gus.BacklogClient import BacklogClient
from gus.Gus import NoRecordException
from ci.jenkins import MrHat
import sys

class CommitMessage:
    '''
    Use this from a the commit-msg git commit hook by calling the validate method
    
        #!/usr/bin/env python
        import sys
        from git.Git import CommitMessage
        cm = CommitMessage()
        cm.validate(sys.argv[1])
        
    '''
    def __init__(self):
        self.validators = []
        self.validators.append(GusValidator())
        self.validators.append(InProgressValidator())
        self.validators.append(BuildValidator())

    def validate(self, msg_file):
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
    def validate(self, comment):
        messages = []
        annotations = comment.annotations()
        if 'fixes' in annotations:
            gus_id = annotations['fixes']
            try:
                gus = BacklogClient()
                work = gus.find_work(gus_id)
                status = work['Status__c']
                
                if status != 'In Progress':
                    messages.append("Work %s status is not In Progress, please update GUS before committing" % gus_id)
            except NoRecordException:
                messages.append("Invalid GUS id: %s.  Please use a valid W# in Gus" % gus_id)
            except:
                messages.append("Can't connect to GUS to check work status.  Connect to vpn before committing.")
                
        return messages
    
class GusValidator:
    def validate(self, comment):
        messages = []
        annotations = comment.annotations()
        
        if 'fixes' in annotations:
            if 'scheduled_build' not in annotations:
                messages.append("You must specify a valid build label for this fix using @scheduled_build or @next")
        else:
            messages.append("All commits should include a GUS work id.  Please annotation your commit with an In Progress GUS id using @fixes")
        
        return messages

