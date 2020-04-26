'''
'''
import sys
import os

import unittest
import pprint
import json
import itertools

import botsley.assets as assets
from botsley.compile.lex.lexer import Lexer
from botsley.compile.parse.parser import Parser
from botsley.compile.ast.node import AstEncoder
from botsley.compile.compiler import Compiler
#
    
def main():
    filename = 'turtles.mia'
    with assets.load(filename) as fh:
        s = fh.read()

    print('##start##')
    print(s)
    print('##end##')
    
    lexer = Lexer()
    tokens = lexer.tokenize(s)
    tokens, tokens2 = itertools.tee(tokens)
    for tok in tokens2:
        print(tok)
    
    parser = Parser()
    #ast = parser.parse(s, debug=1)
    ast = parser.parse(tokens)
    #print ast
    #pprint.pprint(ast)
    #json.dumps(ast)
    print( AstEncoder(indent=2).encode(ast) )
    #
    compiler = Compiler()
    compiler.compile(ast)
        
        
if __name__ == '__main__':
    main()