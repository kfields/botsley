import unittest

from botsley.run.task import *

class Test(unittest.TestCase):
    def test(self):
        with sequence() as s:
            with action() as a:
                async def fn(task, msg):
                    print('Hi')
                a.use(fn)
            with action() as a:
                async def fn(task, msg):
                    print('Bye')
                a.use(fn)

        s.run()

if __name__ == '__main__':
    unittest.main()