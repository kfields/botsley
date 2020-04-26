import unittest

from botsley.run.behavior import *


class Test(unittest.TestCase):
    def test(self):
        with action() as top:
            async def fn(task, msg):
                count = 0
                while True:
                    if count > 4:
                        break 
                    print('act')
                    await task.sleep()
                    count += 1
            top.use(fn)
        top.run()

if __name__ == '__main__':
    unittest.main()