import unittest

from botsley.run.behavior import *

class Test(unittest.TestCase):
    def test(self):
        with action() as a:

            async def fn(task, msg):
                print("Hi")

            a.use(fn)
            a.run()

if __name__ == '__main__':
    unittest.main()
