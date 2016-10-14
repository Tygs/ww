# TODO: add "removable_property" we use in tygs
# TODO: add reify, based on removable property
from past.builtins import basestring


def ensure_tuple(val):
    if not isinstance(val, basestring):
        try:
            return tuple(val)
        except TypeError:
            return (val,)
    return (val,)


def nop(val):
    return val
