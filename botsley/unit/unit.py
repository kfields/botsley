import types
import os

from loguru import logger

def header(text, chr, length):
    count = round((length / 2) - (len(text) / 2))
    mod = length % 2
    return f"{chr * count} {text} {chr * count}"


hlength = 80


def h1(text):
    return header(text, "*", hlength)


def h2(text):
    return header(text, "-", hlength)


def h3(text):
    return header(text, "-", hlength)


def h4(text):
    return header(text, "-", hlength)


class Unit:
    def __init__(self, parent=None):
        self.parent = parent
        self.units = []
        self.logger = logger
        self.loggers = []
    
    def toJSON(self):
        return {filename: self.filename}

    def inject(self, k, v):
        if k == 'module':
            self.module = v
            self.filename = self.module.__file__
            self.dirname = os.path.dirname(self.filename)
            self.basename = os.path.basename(self.filename)
        else:
            self[k] = v

    def config(self, cfg):
        if type(cfg) is types.ModuleType:
            cfg = {'module': cfg}
        for k in cfg:
            v = cfg[k]
            self.inject(k, v)
        return self

    def add(self, child):
        return self.units.append(child)
    
    def push_logger(self, logger):
        self.loggers.append(self.logger)
        self.logger = logger
        return logger

    def pop_logger(self):
        self.logger = logger = self.loggers.pop()
        return logger

    def _(self, txt):
        return self.logger.info(txt)
    
    def debug(self, text):
        return self.debug(text)

    def dataPath(self, filename):
        return path.join(self.dirname, "../data/", filename)

    def logPath(self, filename):
        return path.join(self.dirname, "../report/log/", filename)

    def hf(self):
        return h1(self.basename)

    unit_ = lambda cfg, parent: Unit(parent).config(cfg)
