from jenkinsapi.jenkins import Jenkins
from gus.GusSession import GusSession
import re, httplib, base64, sys, getpass

class MrHat:
    '''
    Interaction with the build server on MrHat to find build numbers, etc
    '''
    def __init__(self):
        session = MrHatSession()
        counter = 0
        self.jenkins = None
        while self.jenkins is None and counter < 3:
            try:
                user = session.load_jenkins_user()
                token = session.load_jenkins_token()
                self.jenkins = Jenkins('http://mrhat.internal.radian6.com/jenkins', user, token)
                self.creds = (user, token)
            except:
                sys.stdin = open('/dev/tty')
                print "Not Logged into Jenkins..."
                user = raw_input("Please enter your Jenkins username: ")
                passwd = getpass.getpass("Please enter your Jenkins password: ")
                token = session.login(user, passwd)
                counter = counter + 1
            
    def get_next_maint_build(self):
        '''
        The next build for the current maint branch
        '''
        return self.get_next_build(branch='maint')
    
    def get_next_head_build(self):
        '''
        The next build for HEAD
        '''
        return self.get_next_build(branch='head')
    
    def get_next_release_build(self):
        '''
        The next build for the current release branch
        '''
        return self.get_next_build(branch='release')
    
    def get_next_build(self, branch='head'):
        '''
        Returns the next build for a specified branch
        '''
        job = self.jenkins['%s-zBuild' % branch]
        build = job.get_last_good_build()
        console = build.get_console()
        release=self.__find_value__("-DreleaseVersion=([^\s]*)", console)
        build=self.__find_value__("-DbuildVersion=([^\s]*)", console)
        b = build.split('_')
        out="MC_%s-%s" % (str(release).replace('-', '.'), self.__increment__(b[0]))
        
        return out
    
    def find_next_build(self, value):
        '''
        Returns the next build for a specified version or assumes the first build
        of an unstarted version
        :Param:value=head,release,maint or a release number
        '''
        if value in ['maint','release','head']:
            build = self.get_next_build(branch=value)
        else:
            build = self.get_next_build_for_version(value)
            
        return build
    
    def get_next_build_for_version(self, version):
        '''
        Compares a supplied version number with what is in head, release and maint
        and returns what is found, otherwise it generates a new build version
        '''
        for i in 'head', 'release', 'maint':
            out = self.get_next_build(branch=i)
            if out.count(version) > 0:
                return out
        return "MC_%s-001" % version
    
    def __increment__(self, build_num):
        '''
        Increments the build number and returns a new zero filled build number
        '''
        if str(build_num).startswith('SP'):
            out = 'SP'
        else:
            out = str(int(build_num) + 1).zfill(3)
            
        return out
        
    def __find_value__(self, pattern, content):
        regex = re.compile(pattern, re.MULTILINE)
        match = regex.search(content)
        out = match.group(1)
        
        return out
    
    def get_current_creds(self):
        '''
        Returns the current creds for MrHat
        '''
        return self.creds
    
class MrHatSession(GusSession):
    def login(self, username, password):
        '''
        Logs into MrHat with a provided username and password and generates a token
        that can be used for subsequent logins.  Persists the token locally.
        '''
        try:
            conn = httplib.HTTPConnection ('mrhat.internal.radian6.com')
            password = password.replace('\n', '')
            auth = base64.encodestring('%s:%s' % (username, password))
            headers = {
                'User-Agent'      : 'mrhat-client',
                'Accept'          : 'text/html',
                'Accept-Encoding' : 'none',
                'Accept-Charset'  : 'utf-8',
                'Connection'      : 'close',
                'Authorization'   : 'Basic %s' % auth,
                }
            conn.request('GET', '/jenkins/user/%s/configure' % username, '', headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
            regex = re.compile("_.apiToken\" value=\"([^\"]*)", re.MULTILINE)
            match = regex.search(data)
            token = match.group(1)
            self.store(jenkinsuser=username, jenkinstoken=token)
        except:
            token = None
            
        return token

    def load_jenkins_token(self):
        '''
        Loads the persisted jenkins token
        '''
        return self.__get_local__('jenkins_token')
    
    def load_jenkins_user(self):
        '''
        Loads the persisted jenkins username
        '''
        return self.__get_local__('jenkins_user')
        
