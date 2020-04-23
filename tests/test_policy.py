import unittest

from botsley.run.policy import Policy


class MyPolicy(Policy):
    @_("+ $x likes Turtles")
    def blah():
        print("blah")

    @_("+ $x likes Turtle Soup")
    def blah():
        print("blah")




class Test(unittest.TestCase):
    def test(self):
        policy = MyPolicy()

        print(vars(policy.__class__))


if __name__ == "__main__":
    unittest.main()
