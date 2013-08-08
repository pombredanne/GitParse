import httplib, re, base64
from userdata.Store import Store

class JenkinsSession(Store):
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
            self.store(jenkins_user=username, jenkins_token=token)
        except:
            token = None
            
        return token

    def load_jenkins_user(self):
        return self.__get_local__('jenkins_user')
    
    def load_jenkins_token(self):
        return self.__get_local__('jenkins_token')