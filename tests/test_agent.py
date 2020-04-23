import unittest

from botsley.application import create_app
app = create_app()

from botsley.run import *
from botsley.run import _I
from botsley.run.agent import Agent

_jump = term_('jump')
_say = term_('say')
_x_ = var_('x')

class MyAgent(Agent):
    def __init__(self):
        super().__init__()
        #print(self.__class__.rules)
        self.post(attempt_(Achieve, _I, _jump))

    @_(OnAttempt(Achieve, _I, _jump))
    async def howhigh(self, msg):
        print('How high?')
        print(msg)

    @_(OnAttempt(Achieve, _I, _say, _x_))
    async def howdy(self, msg):
        print('Howdy Folks!')
        print(msg)

    @_(OnAttempt(Achieve, _I, _say, _x_))
    async def howfar(self, msg):
        print('How Far?')
        print(msg)

class Test(unittest.TestCase):
    def test(self):
        agent = MyAgent()
        agent.run()

if __name__ == '__main__':
    unittest.main()