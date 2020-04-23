import unittest

from botsley.run import *
from botsley.run.policy import Rule

_Bob = term_("Bob")
_likes = term_("likes")
_Fish = term_("Fish")

_Joe = term_("Joe")
_likes = term_("likes")
_Turtles = term_("Turtles")

_x = var_("x")


class Test(unittest.TestCase):
    def test(self):
        c = Believe(_Bob, _likes, _Fish)
        print(c)
        m = Assert(c)
        print(m)

        t = Trigger(Assert, Believe, _Bob, _likes, _Fish)
        print(t.match(m))

        t = Trigger(Assert, Believe, _Joe, _likes, _Fish)
        print(t.match(m))

        t = Trigger(Assert, Believe, _x, _likes, _Fish)
        print(t.match(m))

        async def action(task, msg):
            print("Pow!")

        r = Rule(t, action)

        print(r.match(m))

if __name__ == "__main__":
    unittest.main()
