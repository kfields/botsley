from loguru import logger

from ..task import Method
from .helpers import *


class Neuron:
    def __init__(self):
        self.task = None

    @property
    def activity(self):
        level = self.main()
        logger.debug(f"neuron level: {level}")
        return level

    def main(self):
        return 1

    def use(self, fn):
        self.main = Method(self, fn)


@contextmanager
def neuron(neuron=None):
    if not neuron:
        neuron = Neuron()
    ctx = neuron_ctx_enter(neuron)
    yield neuron
    neuron_ctx_exit(ctx)


"""
#
# Condition
#
class Condition(Neuron):
    def main(self):
        activity = super().main()
        for child in self.children:
            activity *= child.activity
        return activity

@contextmanager
def condition(neuron=None):
    if not neuron:
        neuron = Condition()
    ctx = neuron_ctx_enter(neuron)
    yield neuron
    neuron_ctx_exit(ctx)


condition_ = lambda: Condition()
"""

