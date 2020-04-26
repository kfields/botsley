from .unit import Unit


class Package(Unit):
    def __init__(self, parent):
        super().__init__(parent)

    def inject(self, k, v):
        if k == "blah":
            return this.log("blah")
        else:
            return super().inject(k, v)


package_ = lambda cfg, parent=None: Package(parent).config(cfg)
