import sys
import unittest

from botsley.run import *
from botsley.run.context.yaml import *
from botsley.assets import asset

from tests.common import *

_module = sys.modules[__name__]
_unit = unit_(_module, package)
logger = _unit.logger

for k in defs:
    v = defs[k]
    setattr(_module, k, v)

__ = None

class Test(unittest.TestCase):
    def test(self):
        ctx = yamlcontext_().load(asset('cleavers.yml'))

        logger.info(h2("All Clauses"))
        logger.info(str(ctx))

        logger.info(h2('Binders'))

        _x_ = Variable('$x')
        _d_ = Variable('$d')
        _w_ = Variable('$w')

        logger.info("ctx.query Believe, $x, dad, $d")

        ctx.query(Believe, _x_, _dad, _d_) \
            .exec(lambda binder: logger.info(binder))

        logger.info('ctx.query Believe, $x, dad, $d .and Believe, $d, wife, $w')
        
        ctx.query(Believe, _x_, _dad, _d_) \
            ._and(Believe, _d_, _wife, _w_) \
            .exec(lambda binder: logger.info(binder))

if __name__ == "__main__":
    unittest.main()
