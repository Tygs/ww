# coding: utf-8
# TODO: add "removable_property" we use in tygs
# TODO: add __all__ ?
# TODO: add reify, based on removable property
# TODO: add a function always_return(x) that returns always x, identity
# maybe in a fn module ?
# TODO: doc and test

from functools import partial
from textwrap import dedent

from past.builtins import basestring
from future.utils import bind_method

try:
    unicode = unicode  # type: ignore
except NameError:
    unicode = str

import ww

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


def ensure_callable(value):
    if callable(value):
        return value
    return lambda: value


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

    if len(old_names) != len(new_names):
        raise ValueError(ww.f >> """
           You provided {len(old_names)} old names ("{"', '".join(old_names)}")
           and {len(new_names)} new names ("{"', '".join(new_names)}"). You
           must provide the same number of each.
        """)

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


# Snippet from functools module by Nick Coghlan <ncoghlan at gmail.com>,
# Raymond Hettinger <python at rcn.com>,
# and Łukasz Langa <lukasz at langa.pl>.
# Backported to get fixes from 3.5 in 2.7
#   Copyright (C) 2006-2013 Python Software Foundation.
# See C source code for _functools credits/copyright

WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__qualname__', '__doc__',
                       '__annotations__')
WRAPPER_UPDATES = ('__dict__',)


def update_wrapper(wrapper,
                   wrapped,
                   assigned=WRAPPER_ASSIGNMENTS,
                   updated=WRAPPER_UPDATES):
    """Update a wrapper function to look like the wrapped function

       wrapper is the function to be updated
       wrapped is the original function
       assigned is a tuple naming the attributes assigned directly
       from the wrapped function to the wrapper function (defaults to
       functools.WRAPPER_ASSIGNMENTS)
       updated is a tuple naming the attributes of the wrapper that
       are updated with the corresponding attribute from the wrapped
       function (defaults to functools.WRAPPER_UPDATES)
    """
    for attr in assigned:
        try:
            value = getattr(wrapped, attr)
        except AttributeError:
            pass
        else:
            setattr(wrapper, attr, value)
    for attr in updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
    # Issue #17482: set __wrapped__ last so we don't inadvertently copy it
    # from the wrapped function when updating __dict__
    wrapper.__wrapped__ = wrapped
    # Return the wrapper so this can be used as a decorator via partial()
    return wrapper


def wraps(wrapped,
          assigned=WRAPPER_ASSIGNMENTS,
          updated=WRAPPER_UPDATES):
    """Decorator factory to apply update_wrapper() to a wrapper function

       Returns a decorator that invokes update_wrapper() with the decorated
       function as the wrapper argument and the arguments to wraps() as the
       remaining arguments. Default arguments are as for update_wrapper().
       This is a convenience function to simplify applying partial() to
       update_wrapper().
    """
    return partial(update_wrapper, wrapped=wrapped,
                   assigned=assigned, updated=updated)


def auto_methods(wrapper_class, original_class, methods, force_chaining=False):

    # Add methods with the result being converted automatically to the
    # wrapper class
    for name in methods:

        # Get the original class method reference
        method = getattr(original_class, name)

        # Use a factory to have a parameter with the same name as the local
        # variable and avoid a closure which would always reference the same
        # method
        def factory(method):

            # this is about turning the method into a chaining one
            if force_chaining:

                # This wraps the original class method so it returns self
                @wraps(method)
                def wrapper(self, *args, **kwargs):
                    # type(...) -> wrapper_class
                    method(self, *args, **kwargs)
                    return self

            # this is about wrapping the result
            else:
                # This wraps the original class method so it returns a wrapper
                # class
                @wraps(method)
                def wrapper(*args, **kwargs):
                    # type(...) -> wrapper_class
                    return wrapper_class(method(*args, **kwargs))

            return wrapper

        # Build the wrapper with the proper method passed as a reference
        wrapper = factory(method)

        # Make sure we have a docstring stating this is an automatic method, but
        # include the original docstring in it just in case.

        wrapper.__doc__ = dedent("""
        Same as {wrapper_name}.{name}(), but return a {original_class_name}

        This method has been converted automatically, but the behavior is
        exactly the same than the original method, except we wrap the result in
        a {original_class_name}.

        Here is the original docstring:

        '''
        {method.__doc__}
        '''
        """).strip().format(
            original_class_name=original_class.__class__.__name__,
            wrapper_name=wrapper_class.__class__.__name__,
            method=method,
            name=name
        )

        # Attach our new method to s()
        bind_method(wrapper_class, name, wrapper)
