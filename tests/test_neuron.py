import unittest

from botsley.run.behavior import *


class Test(unittest.TestCase):
    def test(self):
        with counter(1, 11) as cntr:
            with neuron() as c:

                def fn(neuron):
                    if cntr.count > 5:
                        return 0
                    print("good")
                    return 1

                c.use(fn)
                with action() as a:

                    async def fn(task, msg):
                        print(f"neuron: {task.neuron}")
                        print("a count: ", cntr.count)

                    a.use(fn)

        cntr.run()


if __name__ == "__main__":
    unittest.main()
