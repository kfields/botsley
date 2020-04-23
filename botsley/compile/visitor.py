import json

from botsley.compile.policy import Policy
from botsley.compile.ast.node import Node


class Visitor(Policy):
    def __init__(self, parent=None, iterable=(), **kwargs):
        super().__init__(parent, iterable, **kwargs)
        self.policy = self  # talk about circularities
        self.stack = []

    def top(self, ndx=0):
        return self.stack[len(self.stack) + (ndx - 1)]

    def policy_(self, delegates):
        self.policy = policy = Policy(self.policy, delegates)
        return policy

    def visit_node(self, node):
        child = None
        if not node:
            return
        if isinstance(node, list):
            for child in node:
                self.visit(child)
            return
        if not isinstance(node, Node):
            raise Exception("Not a node!", node)
        for child in node.nodes:
            self.visit(child)

    def visit(self, node):
        if not node:
            # print(self)
            # raise Error(self)
            return
        if not isinstance(node, Node):
            raise Exception("Not a node!", node, node.__class__)
        #print(node, node, node.__class__)
        result = None
        self.save()
        self.stack.append(node)
        delegate = self.policy[node.kind]
        if not delegate:
            result = self.visit_node(node)
        else:
            result = delegate(node)

        self.stack.pop()
        self.restore()
        return result
