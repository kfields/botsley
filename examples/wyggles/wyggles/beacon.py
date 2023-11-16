from .sprite import Sprite

class Beacon():
    def __init__(self, sprite: Sprite, type: str):
        self.sprite: Sprite = sprite
        self.type: str = type

    @property
    def position(self):
        return self.sprite.position

    @position.setter
    def position(self, val):
        self.sprite.position = val

    @property
    def x(self):
        return self.sprite.position[0]

    @property
    def y(self):
        return self.sprite.position[1]
