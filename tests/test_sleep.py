import unittest

from botsley.run.behavior import *


class Test(unittest.TestCase):
    def test_sleep_0(self):
        with action() as top:
            async def fn(task, msg):
                count = 0
                while True:
                    if count > 4:
                        break 
                    print(count)
                    await task.sleep()
                    count += 1
            top.use(fn)
        top.run()

    def test_sleep_1(self):
        with action() as top:
            async def fn(task, msg):
                count = 0
                while True:
                    if count > 4:
                        break 
                    print(count)
                    await task.sleep(.1)
                    count += 1
            top.use(fn)
        top.run()

if __name__ == '__main__':
    unittest.main()