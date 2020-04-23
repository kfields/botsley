import unittest

import botsley.compile.ast.node as yy

class Test(unittest.TestCase):
    def test(self):
        obj = yy.Term('Bob')
        print(vars(obj), obj.__class__)

        obj = yy.term_('Joe')
        print(vars(obj), obj.__class__)

        obj = yy.Type('Eggs')
        print(vars(obj), obj.__class__)

        obj = yy.type_('Bacon')
        print(vars(obj), obj.__class__)

        obj = yy.Term('Henry')
        print(vars(obj), obj.__class__)

        obj = yy.term_('Frank')
        print(vars(obj), obj.__class__)

if __name__ == '__main__':
    unittest.main()