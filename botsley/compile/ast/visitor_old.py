

class Visitor(object):
    def __init__(self):
        pass

    def visit(self, node):
        policy = self.policies[node.kind];
        if policy == None:
            print(node)
            raise Exception("Undefined Policy:  " + node.kind)
        policy.begin(self, node)
        policy.end(self, node)
        