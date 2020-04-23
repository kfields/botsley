class Policy:
    # this allows us to create from dictionary or keywords
    def __init__(self, parent=None, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)
        self.parent = parent
    '''
    def __init__(self, parent=None):
        self.parent = parent
    '''
    def __getitem__(self, key):
            if hasattr(self, key):
                return getattr(self, key)
            if self.parent:
                return self.parent[key]

