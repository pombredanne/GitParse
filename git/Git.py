import subprocess, re

class Author:
    '''
    Finds the committer name and email from the log for the specified commit.  Assumes last commit
    unless specified
    '''
    a_name = ''
    a_email = ''

    def __init__(self, commitid='-1'):
        author = subprocess.check_output(['git','log',commitid,'--pretty=format:%cn,%ce'])
        self.a_name, self.a_email = author.split(",")

    def name(self):
        return self.a_name

    def email(self):
        return self.a_email

class Comment:
    '''
    Processes the commit message in a specified commit.  The subject() is the first line of the commit
    and body() is the remaining lines.  Annotations are returned as a map.
    '''
    title = ''
    overview = ''

    def __init__(self, comment=None, commitid='-1'):
        if comment is None:
            out = subprocess.check_output(['git', 'log', commitid, '--pretty=format:%B'])
            out = out.replace('"', '')
        else:
            out = comment
            
        commit_array = out.split("\n")
        self.title, self.overview = commit_array[0], "\n".join(commit_array[1:])

    def subject(self):
        '''
        First line of the commit message
        '''
        return self.title

    def body(self):
        '''
        Second and subsequent lines of the commit message
        '''
        return self.overview
    
    def annotations(self):
        '''
        Map of annotations found in the commit message in the format '@key value'
        '''
        out = {}
        regex = re.compile("@([^\s]*) ([^\s]*)",re.MULTILINE)
        
        for k, v in regex.findall(self.title):
            out[k] = v
        for k, v in regex.findall(self.overview):
            out[k] = v

        return out

class Changes:
    '''
    Outputs changed files in a given commit.  Assumes last commit unless specified
    '''
    def list(self, commitid='-1'):
        changelist = subprocess.check_output(['git', 'log', commitid, '--name-status', '--pretty=format:%cd'])
        changelist = changelist.replace('\t',': ')
        changes = changelist.split("\n")
        # removes the first line of the output so that all left is the changelist
        changeout = "\n".join(changes[1:])
        return changeout

class Patch:
    '''
    Creates a unified diff of the last commit
    '''
    def diff(self, commitid='-1'):
        diff = subprocess.check_output(['git','log',commitid,'--unified=100000','--pretty=format:%cd'])
        diff_array = diff.split("\n")
        # removes the first line of the output so all that is left is the diff
        diffout = "\n".join(diff_array[1:])
        return diffout
    
    

