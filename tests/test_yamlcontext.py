import unittest

from botsley.run import *
from botsley.run.context.yaml import YamlContext
from botsley.assets import asset

class Test(unittest.TestCase):
    def test(self):
        ctx = YamlContext().load(asset('cleavers.yml'))
        print(ctx)

if __name__ == '__main__':
    unittest.main()
