import unittest
from ..Git import Comment
from ..Git import PostCommit

class Test(unittest.TestCase):

    def test_that_annotations_can_be_instantiated(self):
        comment = Comment(comment='this is a test @test 1234 stuff')
        self.assertEqual('1234', comment.annotations()['test'], 'Got the wrong value for annotation')
        
    def test_rehydrated_session(self):
        commit = {
               'annotations' : {'gus_session':'something', 'scheduled_build':'something', 'fixes':'something'}
               }
        pc = PostCommit()
        pc.gus(commit)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()