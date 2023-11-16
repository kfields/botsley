from loguru import logger

from botsley.run import *
from botsley.run import _I
from botsley.run.behavior import *

from wyggles.mathutils import *
from wyggles.engine import *
from wyggles.wyggle.brain import WyggleBrain
from wyggles.fruit import Fruit
from wyggles.ball import Ball

_see = term_('see')

class SeesFood(Neuron):
    def __init__(self):
        super().__init__()
        self.focus = None

    def main(self):
        logger.debug(f"I see food")
        beacons = sprite_engine.query(self.bot.x, self.bot.y, self.bot.sensor_range)
        self.focus = None
        for beacon in beacons:
            if isinstance(beacon.sprite, Fruit):
                self.focus = beacon.sprite
                break
        else:
            return 0
        return 1

class MoveTo(Action):
    def __init__(self, sees):
        super().__init__()
        self.sees = sees

    async def main(self, msg: Message):
        self.bot.focus = focus = self.sees.focus
        self.bot.state = 'move_to'
        while self.ok():
            if self.bot.sprite.intersects(focus):
                self.bot.state = ''
                return self.succeed()
            self.bot.move_to(focus.position)
            await self.sleep()

class Eat(Action):
    def __init__(self, sees):
        super().__init__()
        self.sees = sees

    async def main(self, msg: Message):
        self.bot.focus = focus = self.sees.focus
        self.bot.state = 'eat'
        
        while self.ok():
            if focus.is_munched():
                sprite = self.bot.sprite
                sprite.close_mouth()
                sprite.energy = sprite.energy + focus.energy
                self.bot.reset()
                return self.succeed()
            await self.sleep()

class SeesBall(Neuron):
    def __init__(self):
        super().__init__()
        self.focus = None

    def main(self):
        logger.debug(f"I see a ball")
        beacons = sprite_engine.query(self.bot.x, self.bot.y, self.bot.sensor_range)
        self.focus = None
        for beacon in beacons:
            if isinstance(beacon.sprite, Ball):
                self.focus = beacon.sprite
                break
        else:
            return 0
        return 1

class Kick(Action):
    def __init__(self, sees):
        super().__init__()
        self.sees = sees

    async def main(self, msg: Message):
        self.bot.focus = focus = self.sees.focus
        self.bot.state = 'kick'
        focus.receive_kick(self.bot.heading, 200)
        self.bot.reset()

class Wander(Action):
    async def main(self, msg: Message):
        self.bot.state = 'wander'
        while self.ok():
            await self.sleep()
            return self.fail()

class NeuronBrain(WyggleBrain):
    def __init__(self, model):
        super().__init__(model)
        with root(self):
            with forever():
                with selector():
                    with neuron(SeesFood()) as sees_food:
                        with sequence():
                            with action(MoveTo(sees_food)):
                                pass
                            with action(Eat(sees_food)):
                                pass
                    
                    with neuron(SeesBall()) as sees_ball:
                        with sequence():
                            with action(MoveTo(sees_ball)):
                                pass
                            with action(Kick(sees_ball)):
                                pass

                    with action(Wander()):
                        pass

    def update(self, delta_time: float = 1 / 60):
        super().update(delta_time)
        state = self.state
        if state == "wander":
            self.state_wander()
        elif state == "move_to":
            self.state_move_to()
        elif state == "eat":
            self.state_eat()
        elif state == "kick":
            self.state_kick()

    def state_wander(self):
        if self.at_goal():
            pt = math.floor(random.random() * 3)
            pd = math.floor(random.random() * 45)
            if pt == 0:
                self.left(pd)
            elif pt == 2:
                self.right(pd)
            self.project(self.sensor_range)
        self.move()

    def state_move_to(self):
        self.move()

    def state_eat(self):
        if self.munch_timer > 0:
            self.munch_timer -= 1
            return
        else:
            self.munch_timer = 10

        if self.sprite.face != "munchy":
            self.sprite.open_mouth()
        else:
            self.sprite.close_mouth()
            self.focus.receive_munch()

    def state_kick(self):
        self.move()
