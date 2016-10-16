# TODO: add "removable_property" we use in tygs
# TODO: add reify, based on removable property
from past.builtins import basestring

try:
    unicode = unicode  # type: ignore
except NameError:
    unicode = str


def ensure_tuple(val):
    if not isinstance(val, basestring):
        try:
            return tuple(val)
        except TypeError:
            return (val,)
    return (val,)


def nop(val):
    return val


def require_positive_number(number, name,
                            tpl='{} must be a positive number or 0, not "{}"'):
    try:
        number = int(number)
    except ValueError:
        raise ValueError(tpl.format(name, number))

    if number < 0:
        raise ValueError(tpl.format(name, number))

    return number
