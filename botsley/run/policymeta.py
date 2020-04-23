class PolicyMetaDict(dict):
    '''
    Dictionary that allows decorated grammar rule functions to be overloaded
    '''
    def __setitem__(self, key, value):
        if key in self and callable(value) and hasattr(value, 'triggers'):
            value.next_func = self[key]
            if not hasattr(value.next_func, 'triggers'):
                raise GrammarError(f'Redefinition of {key}. Perhaps an earlier {key} is missing @_')
        super().__setitem__(key, value)
    
    def __getitem__(self, key):
        if key not in self and key.isupper() and key[:1] != '_':
            return key.upper()
        else:
            return super().__getitem__(key)

def _decorator(trigger, *extra):
     triggers = [trigger, *extra]
     def decorate(func):
         func.triggers = [ *getattr(func, 'triggers', []), *triggers[::-1] ]
         return func
     return decorate

class PolicyMeta(type):
    @classmethod
    def __prepare__(meta, *args, **kwargs):
        d = PolicyMetaDict()
        d['_'] = _decorator
        return d

    def __new__(meta, clsname, bases, attributes):
        del attributes['_']
        cls = super().__new__(meta, clsname, bases, attributes)
        cls._build(list(attributes.items()))
        return cls
