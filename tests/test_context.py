import unittest

from botsley.run import *
from botsley.run.context import Context

_Bob = term_('Bob')
_likes = term_('likes')
_Toast = term_('Toast')

class Test(unittest.TestCase):
    def test(self):
        ctx = Context()
        ctx.add(believe_(_Bob, _likes, _Toast))
        print(ctx)

if __name__ == '__main__':
    unittest.main()