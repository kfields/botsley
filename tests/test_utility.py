import unittest

from botsley.run.behavior import *


class Test(unittest.TestCase):
    def test(self):
        with counter(1, 11) as cntr:
            with utility() as util:
                with neuron() as n:

                    def fn(neuron):
                        if cntr.count > 5:
                            return 0
                        print("low")
                        return 1

                    n.use(fn)
                    with action() as a:

                        async def fn(task, msg):
                            print(f"neuron: {task.neuron}")
                            print("a count: ", cntr.count)

                        a.use(fn)

                with neuron() as n:

                    def fn(neuron):
                        if cntr.count < 5:
                            return 0
                        print("high")
                        return 1

                    n.use(fn)
                    with action() as b:

                        async def fn(task, msg):
                            print(f"neuron: {task.neuron}")
                            print("b count: ", cntr.count)

                        b.use(fn)

        cntr.run()


if __name__ == "__main__":
    unittest.main()
