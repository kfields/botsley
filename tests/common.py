from botsley.run import *
from botsley.unit import *

defs = term_([
  'Bob',
  'Joe',
  'Fish',
  'Chips',
  'Tuna',
  'Cheese',
  'Peas',

  'exists',
  'on',
  'age',
  'likes',
  'get',
  'catch',
  'buy',
  'eat',

  'dad',
  'mom',
  'brother',
  'wife'
])

_module = __import__(__name__)

def inject_defs(module):
  for k in defs:
      v = defs[k]
      setattr(module, k, v)
  setattr(module, '__', None)

inject_defs(_module)

package = package_(_module)
unit_ = lambda cfg, parent=package: Unit(parent).config(cfg)

#__all__ = [x for x in dir(_module) if not x.startswith('__')]
#print(__all__)
#__all__ = dir(defs)
#__all__ = dir(_module)
#print(__all__)