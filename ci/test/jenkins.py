'''
Created on Jul 26, 2013

@author: scrosby
'''
import unittest
from ..jenkins import MrHatSession


class Test(unittest.TestCase):


    def test_mr_hat_session(self):
        mrhat = MrHatSession(filename=".test_data")
        token = mrhat.login('scrosby', 'Ih@techangingpassw0rds')
        print 'token: %s' % token


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()