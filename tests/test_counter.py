import unittest

from botsley.run.behavior import *


class Test(unittest.TestCase):
    def test(self):
        with counter(1, 11) as top:
            with action() as a:
                async def fn(task, msg):
                    print('count: ',task.parent.count)
                a.use(fn)
        top.run()

if __name__ == '__main__':
    unittest.main()