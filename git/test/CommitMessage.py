'''
Created on Jul 26, 2013

@author: scrosby
'''
import unittest
from ..CommitMessage import BuildValidator
from ..Git import Comment


class Test(unittest.TestCase):


    def test_build_validator(self):
        
        bv = BuildValidator()
        out = bv.validate(Comment(comment='no scheduled build'))
        print out


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()