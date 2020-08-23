import unittest

from botsley.run.behavior import *


class Test(unittest.TestCase):
    def test(self):
        with selector() as s:
            with action() as a:
                async def fn(task, msg):
                    print('I failed')
                    return task.fail()
                a.use(fn)
            with action() as b:
                async def fn(task, msg):
                    print('Bye')
                b.use(fn)

        s.run()

if __name__ == '__main__':
    unittest.main()