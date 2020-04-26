from .unit import Unit


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

class TestUnit(Unit):
    def dataPath(self, filename):
        return path.join(self.dirname, "../data/", filename)

    def logPath(self, filename):
        return path.join(self.dirname, "../report/log/", filename)

    def hf(self):
        return h1(self.basename)

testunit_ = lambda: TestUnit()
