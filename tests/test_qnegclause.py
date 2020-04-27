import sys
import unittest

from botsley.run import *
from botsley.run.context.yaml import *
from botsley.assets import asset

from tests.common import *

_module = sys.modules[__name__]
_unit = unit_(_module, package)
logger = _unit.logger

inject_defs(_module)

class Test(unittest.TestCase):
    def test(self):
        ctx = yamlcontext_().load(asset('bob.yml'))

        logger.info(h2("All Clauses"))
        logger.info(str(ctx))

        logger.info(h2('Binders'))
        _x_ = Variable('$x')
        _y_ = Variable('$y')
        _z_ = Variable('$z')

        logger.info('''
        ctx.query Believe, _$x, _likes, _$y
        .not Believe, _$x, _likes, _Chips
        '''
        )
        ctx.query(Believe, _x_, _likes, _Fish) \
            ._not(Believe, _x_, _likes, _Chips) \
            .exec(lambda binder: logger.info(binder))

if __name__ == "__main__":
    unittest.main()
