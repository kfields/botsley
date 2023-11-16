from typing import Any, Callable, List, Optional, Union, Coroutine
import random
import copy

import pymunk

from .layer import Layer

from wyggles.mathutils import *
from .beacon import Beacon

world_left = 0
world_bottom = 0
# world_right = 1024
world_right = 800
# world_top = 768
world_top = 600


def materialize_random_from_center(sprite):
    halfMaxX = world_right / 2
    halfMaxY = world_top / 2
    diameter = world_top
    radius = diameter / 2
    sprite.materialize_at(
        (halfMaxX - radius) + (random.random() * diameter),
        (halfMaxY - radius) + (random.random() * diameter),
    )


class SpriteEngine:
    def __init__(self):
        self.root = Layer("root")
        #
        self.beacons: List[Beacon] = []
        self.id_counter: int = 0
        #
        self.gravity_x: float = 0
        # self.gravity_y = 9.8 ;
        self.gravity_y: float = 0
        # new stuff
        self.space = pymunk.Space()
        self.space.iterations = 35
        self.space.gravity = (self.gravity_x, self.gravity_y)

    def add_beacon(self, beacon):
        self.beacons.append(beacon)

    def remove_beacon(self, beacon):
        if beacon in self.beacons:
            self.beacons.remove(beacon)

    def query(self, x, y, distance):
        result = []
        for beacon in self.beacons:
            dist = distance2d((x, y), (beacon.x, beacon.y))
            if dist < distance:
                b = copy.copy(beacon)
                b.distance = dist
                result.append(b)
        result.sort(key=lambda x: x.distance)
        return result

    def gen_id(self, name):
        result = name + str(self.id_counter)
        self.id_counter += 1
        return result

    def get_root(self):
        return self.root


sprite_engine = SpriteEngine()
