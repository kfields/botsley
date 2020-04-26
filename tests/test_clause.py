import unittest

from botsley.run import *

_Bob = term_("Bob")
_likes = term_("likes")
_Fish = term_("Fish")
_and = term_("and")
_Chips = term_("Chips")

class Test(unittest.TestCase):
    def test_simple(self):
        c = believe_(_Bob, _likes, _Fish)
        print(c)

    def test_xtra(self):
        c = believe_(_Bob, _likes, _Fish, _and=_Chips)
        print(c)

if __name__ == '__main__':
    unittest.main()