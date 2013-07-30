#!/usr/bin/env python
import os, shutil


def main():
    cwd = os.getcwd()
    script_dir = os.path.dirname(__file__)
    hooks_dir = os.path.join(cwd, '.git/hooks')
    
    if os.path.exists(hooks_dir):
        shutil.copy(os.path.join(script_dir, 'commit-msg'), hooks_dir)
        os.chmod(os.path.join(hooks_dir, 'commit-msg'), 0755)
        shutil.copy(os.path.join(script_dir, 'post-commit'), hooks_dir)
        os.chmod(os.path.join(hooks_dir, 'post-commit'), 0755)
    else:
        print "No Git Repo in this directory.  Move to the root of the git repo and try again"
        
if __name__ == '__main__':
    main()
