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
        ctx = yamlcontext_().load(asset('blocks.yml'))
        _Block = term_('Block')
        logger.info(h2("All Clauses"))
        logger.info(str(ctx))

        logger.info(h2('Binders'))
        _x_ = Variable('$x', lambda v: isinstance(v, _Block))
        _y_ = Variable('$y')

        logger.info("ctx.query Believe, $x, _on, $y")
        ctx.query(Believe, _x_, _on, _y_) \
            .exec(lambda binder: logger.info(binder))

if __name__ == "__main__":
    unittest.main()
