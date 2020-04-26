import unittest

import botsley.assets as assets
from botsley.compile.lex.lexer import Lexer

class Test(unittest.TestCase):
    def test(self):
        filename = "turtles.mia"

        with assets.load(filename) as fh:
            s = fh.read()
            print('string', s)
            
        lexer = Lexer()
        tokens = lexer.tokenize(s)
        for tok in tokens:
            print(tok)


if __name__ == "__main__":
    Test().test()
