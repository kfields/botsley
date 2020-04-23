class MetaNode(type):
    nodeCount = 0
    # def __init__(self):
    # def __new__(cls, name, bases, attr):
    def __init__(cls, name, bases, attr):
        cls.nodeCount = 0

    @classmethod
    def node(self, name):
        index = self.nodeCount
        self.nodeCount += 1

        def getter(self):
            return self.nodes[index]

        def setter(self, val):
            self.nodes[index] = val

        prop = property(getter, setter)
        setattr(self, name, prop)
