import unittest

from botsley.run.task import *


class Test(unittest.TestCase):
    def test(self):
        with timer(0.5) as top:
            with loop() as l:
                with counter(1, 11) as cntr:
                    with condition() as c:

                        async def fn(task, msg):
                            if cntr.count > 5:
                                return task.fail()
                            print("good")

                        c.use(fn)
                    with action() as a:

                        async def fn(task, msg):
                            print("a count: ", cntr.count)

                        a.use(fn)

        top.run()


if __name__ == "__main__":
    unittest.main()
