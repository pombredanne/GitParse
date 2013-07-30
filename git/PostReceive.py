
class PostReceive:
    '''
    Processes webhooks from GitHub
    '''
    def process(self, json_data):
        commits = json_data['commits']
        for commit in commits:
            print 'Commit: [%s - %s] pushed to GitHub' % (commit['id'], commit['message'])
            for add in commit['added']:
                print '\tAdded: %s' % add
                
            for mod in commit['modified']:
                print '\tModified: %s' % mod
                
            for delete in commit['removed']:
                print '\tRemoved: %s' % delete
