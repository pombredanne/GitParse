'''
Created on Jul 29, 2013

@author: scrosby
'''
import unittest
from ..PostCommit import PostCommit

class Test(unittest.TestCase):
    def setUp(self):
        self.commit = {}
        self.commit['annotations'] = {}
        self.pc = PostCommit()

    def test_fix_is_valid_when_fixes_and_scheduled_build(self):
        self.commit['annotations']['fixes'] = 'W-123456'
        self.commit['annotations']['scheduled_build'] = 'MC_185'
        out = self.pc.__is_valid_fix__(self.commit)
        self.assertTrue(out)
        
    def test_fix_is_valid_when_fixes_and_next(self):
        self.commit['annotations']['fixes'] = 'W-123456'
        self.commit['annotations']['next'] = 'head'
        out = self.pc.__is_valid_fix__(self.commit)
        self.assertTrue(out)
        
    def test_fix_is_not_valid_when_fixes_only(self):
        self.commit['annotations']['fixes'] = 'W-123456'
        out = self.pc.__is_valid_fix__(self.commit)
        self.assertFalse(out)
        
    def test_fix_is_not_valid_without_fixes(self):
        self.commit['annotations']['next'] = 'head'
        out = self.pc.__is_valid_fix__(self.commit)
        self.assertFalse(out)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testame']
    unittest.main()