import unittest

from botsley.run.behavior import *


class Test(unittest.TestCase):
    def test(self):
        with action() as top:
            async def fn(task, msg):
                while True:
                    print('act')
                    await task.sleep()
            top.use(fn)
        top.run()

if __name__ == '__main__':
    unittest.main()