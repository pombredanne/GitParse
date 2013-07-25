from jenkinsapi.jenkins import Jenkins
import re

class MrHat:
    def get_next_maint_build(self):
        return self.get_next_build(branch='maint')
    
    def get_next_head_build(self):
        return self.get_next_build(branch='head')
    
    def get_next_release_build(self):
        return self.get_next_build(branch='release')
    
    def get_next_build(self, branch='head'):
        jenkins = Jenkins('http://mrhat.internal.radian6.com/jenkins', 'scrosby', 'Ih@techangingpassw0rds')
        job = jenkins['%s-zBuild' % branch]
        build = job.get_last_good_build()
        console = build.get_console()
        release=self.__find_value__("-DreleaseVersion=([^\s]*)", console)
        build=self.__find_value__("-DbuildVersion=([^\s]*)", console)
        b, n = build.split('_')
        out="MC_%s-%s" % (str(release).replace('-', '.'), self.__increment__(b))
        
        return out
    
    def find_next_build(self, value):
        if value in ['maint','release','head']:
            build = self.get_next_build(branch=value)
        else:
            build = self.get_next_build_for_version(value)
            
        return build
    
    def get_next_build_for_version(self, version):
        for i in 'head', 'release', 'maint':
            out = self.get_next_build(branch=i)
            if out.count(version) > 0:
                return out
        return "MC_%s-001" % version
    
    def __increment__(self, build_num):
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

