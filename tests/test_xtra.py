import sys
import unittest

from botsley.run import *
from botsley.run.context import *

from tests.common import *

_module = sys.modules[__name__]
_unit = unit_(_module, package)
logger = _unit.logger

inject_defs(_module)

class Test(unittest.TestCase):
    def test(self):

        ctx = context_()
        c1 = believe_(_Bob, _likes, _Tuna, _with=_Cheese)
        ctx.add(c1)
        c2 = believe_(_Joe, _likes, _Peas)
        ctx.add(c2)

        logger.info(h2("All Clauses"))
        for c in ctx.clauses:
            logger.info(str(c))

        logger.info(h2("Find in Context"))
        r = ctx.find(Believe, _Bob, _likes, _Tuna)
        logger.info("< Bob likes Tuna >")
        logger.info(str(r))

        r = ctx.find(Believe, __, _likes, _Tuna)
        logger.info("< __ likes Tuna >")
        logger.info(str(r))

        r = ctx.find(Believe, __, _likes, __)
        logger.info("< __ likes __ >")
        logger.info(str(r))

        logger.info(h2("Message Matches"))
        m = Assert(c1)
        logger.info(m.match(Assert, Believe, __, _likes, _Tuna))
        logger.info(m.match(Assert, Believe, _Bob, _likes, _Tuna))
        logger.info(m.match(Assert, Believe, _Bob, _likes, _Fish))
        logger.info(m.match(Retract, Believe, _Bob, _likes, _Fish))
        logger.info(m.match(Assert, Believe, _Joe, _likes, _Fish))


if __name__ == "__main__":
    unittest.main()
