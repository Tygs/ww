# TODO: add "removable_property" we use in tygs
# TODO: add reify, based on removable property
# TODO: add a function always_return(x) that returns always x, identity
# maybe in a fn module ?
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


# TODO: make that a decorator
# TODO: make name not required
def require_positive_number(number, name,
                            tpl='{} must be a positive number or 0, not "{}"'):
    try:
        number = int(number)
    except (ValueError, TypeError):
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
            for old_name, new_name in zip(old_names, new_names):
                if old_name in kwargs:
                    raise TypeError(('"{}" doesn\'t exist. Instead, '
                                     'use "{}"').format(old_name, new_name))
            return func(*args, **kwargs)
        return decorated
    return decorator
