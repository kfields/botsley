import unittest

from botsley.run import *

_Bob = term_("Bob")
_likes = term_("likes")
_Fish = term_("Fish")

class Test(unittest.TestCase):
    def test(self):
        c = Clause(_Bob, _likes, _Fish)
        print(c)

if __name__ == '__main__':
    unittest.main()