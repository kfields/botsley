import unittest

from botsley.run import *

class Test(unittest.TestCase):
    def test(self):
        bob = term_('Bob')
        print(bob, bob.__class__.__name__)
        bob2 = term_('Bob')

        assert(bob == bob2)

        jump = term_('jump')
        print(jump, jump.__class__.__name__)

if __name__ == '__main__':
    unittest.main()