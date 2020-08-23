from .helpers import *


class method:
    def __init__(self, instance, func):
        self.im_self = instance
        self.im_class = instance.__class__
        self.im_func = func

    def __call__(self, *args, **kw):
        if self.im_self:
            args = (self.im_self,) + args
        return self.im_func(*args, **kw)


class Neuron:
    def __init__(self):
        self.task = None

    @property
    def activity(self):
        level = self.main()
        print(level)
        return level

    def main(self):
        return 1

    def use(self, fn):
        self.main = method(self, fn)


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

