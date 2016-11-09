# TODO: add "removable_property" we use in tygs
# TODO: add reify, based on removable property
from functools import wraps

from past.builtins import basestring

try:
    unicode = unicode  # type: ignore
except NameError:
    unicode = str

# create a @deprecated decorator
# like this one: https://github.com/python/mypy/issues/2403
# which:
# - save the object in a list of deprecated things
# - issue a warning if used
# - check if deprecated is not in the docstring, and add it at the end if
#   not if you pass "add_to_docstring"


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


def renamed_argument(old_names, new_names):

    old_names = ensure_tuple(old_names)
    new_names = ensure_tuple(new_names)

    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if old_names in kwargs:
                if new_names not in kwargs:
                    raise TypeError(('{} argument doesn\'t exist. Instead,'
                                     'use {}').format(old_names, new_names))
                else:
                    raise TypeError(('You gave both {} and {} arguments, '
                                     'but {1} doesn\'t exist.')
                                    .format(old_names, new_names))
            return func(*args, **kwargs)
        return decorated
    return decorator
