# coding: utf-8

# TODO: more test, better doc and type annotations
# TODO: ChainMap
# https://pypi.python.org/pypi/chainmap/1.0.2
# TODO: Counter
# TODO: od for ordereddict
# TODO: sd for sortedict
# TODO: items()/keys()/values() should return a viewwrapper using g()
# TODO: delegate work on utils


from __future__ import (division, absolute_import,
                        print_function, unicode_literals)

import sys
from pprint import pprint

from future.builtins import range

import ww

from ww.types import Iterable, Hashable, Any  # noqa
from ww.utils import ensure_callable


class DictWrapper(dict):

    @classmethod
    def from_iterable(cls, iterable, default=None):
        # TODO : type: (Iterable, Union[Any, Callable]) -> DictWrapper
        # https://github.com/python/mypy/issues/2254
        """ Like fromkeys, but value accept a callable as well.

        Args:
            iterable: Iterable containing keys
            value: value to associate with each key.
            If callable, will be called to generate the key.

        Returns: new DictWrapper

        Example:

            >>> from ww import d
            >>> sorted(d.from_iterable('123', default=4).items())
            [('1', 4), ('2', 4), ('3', 4)]
            >>> sorted(d.from_iterable(range(3), default=lambda e:e**2).items())
            [(0, 0), (1, 1), (2, 4)]
        """
        if not callable(default):
            return cls(cls.fromkeys(iterable, default))

        return cls((key, default(key)) for key in iterable)

    @classmethod
    def from_vars(cls, *names, **kwargs):
        call_frame = sys._getframe(1)
        global_vars = cls(call_frame.f_globals).subset(*names, **kwargs)
        return global_vars +  cls(call_frame.f_locals).subset(*names, **kwargs)

    @classmethod
    def from_range(cls, start=0, stop=None, step=1, **kwargs):

        if stop is None:
            stop = start
            start = 0

        numbers = range(start, stop, step)
        return cls.from_iterable(numbers, default=kwargs.get('default', None))

    def __add__(self, other):
        # type: (dict) -> DictWrapper
        """Add other in self and return new dict

        Args:
            other: dict to add in self

        Returns: Merged dict

        Example:

            >>> from ww import d
            >>> current_dict = d({1: 1, 2: 2, 3: 3})
            >>> to_merge_dict = {3: 4, 4: 5}
            >>> current_dict + to_merge_dict
            {1: 1, 2: 2, 3: 4, 4: 5}
        """
        copy = self.__class__(self.copy())
        return copy.merge(other)

    def __radd__(self, other):
        # type: (dict) -> DictWrapper
        """Add other in self, and return new dict

        Args:
            other: dict to add in self

        Returns: Merged dict

        Example:

            >>> from ww import d
            >>> current_dict = {1: 1, 2: 2, 3: 3}
            >>> to_merge_dict = d({3: 4, 4: 5})
            >>> current_dict + to_merge_dict
            {1: 1, 2: 2, 3: 4, 4: 5}
        """
        copy = self.__class__(other.copy())
        return copy.merge(self)

    def __iadd__(self, other):
        # type: (dict) -> DictWrapper
        """Add other in self

        Args:
            other: Dict to add in self

        Returns: Merged dict

        Example:

            >>> from ww import d
            >>> current_dict = d({1: 1, 2: 2, 3: 3})
            >>> current_dict += {5: 6, 6: 7}
            >>> current_dict
            {1: 1, 2: 2, 3: 3, 5: 6, 6: 7}
        """
        return self.merge(other)

    def __iter__(self):
        """Return the inner iterator

        Returns: iterator

        """
        return iter(ww.g(self.items()))

    def isubset(self, *keys, **kwargs):
        # type: (*Hashable) -> ww.g
        """Return key, self[key] as generator for key in keys.

        Raise KeyError if a key does not exist

        Args:
            keys: Iterable containing keys

        Example:

            >>> from ww import d
            >>> list(d({1: 1, 2: 2, 3: 3}).isubset(1, 3))
            [(1, 1), (3, 3)]
        """
        default = ensure_callable(kwargs.get('default', None))
        return ww.g((key, self.get(key, default())) for key in keys)

    def subset(self, *keys, **kwargs):
        # type: (*Hashable) -> DictWrapper
        """Return d(key, self[key]) for key in keys.

        Raise KeyError if a key does not exist

        Args:
            keys: Iterable containing keys

        Example:

            >>> from ww import d
            >>> d({1: 1, 2: 2, 3: 3}).subset(1,3)
            {1: 1, 3: 3}
        """
        return self.__class__(self.isubset(*keys, **kwargs))

    def swap(self):
        # type: () -> DictWrapper
        """Swap key and value

        /!\ Be carreful, if there are duplicate values, only one will
        survive /!\

        Example:

            >>> from ww import d
            >>> d({1: 2, 2: 2, 3: 3}).swap()
            {2: 2, 3: 3}
        """
        return self.__class__((v, k) for k, v in self.items())

    def add(self, key, value):
        # type: (Hashable, Any) -> DictWrapper
        """Add value in key

        Args:
            key: Key
            value: Value to associate to the key

        Example:

            >>> from ww import d
            >>> current_dict = d({1: 1, 2: 2, 3: 3})
            >>> current_dict.add(4, 5)
            {1: 1, 2: 2, 3: 3, 4: 5}
        """
        self[key] = value
        return self

    def merge(self, other_dict):
        # type: (dict) -> DictWrapper
        """Merge self with other_dict

        Args:
            other_dict: dict to merge with self

        Returns: merged dict

        Example:

            >>> from ww import d
            >>> current_dict = d({1: 1, 2: 2, 3: 3})
            >>> to_merge_dict = d({3: 4, 4: 5})
            >>> current_dict.merge(to_merge_dict)
            {1: 1, 2: 2, 3: 4, 4: 5}
        """
        self.update(other_dict)
        return self

    def delete(self, *keys):
        # type: (*Hashable) -> DictWrapper
        """Delete keys from dict

        Args:
            *keys: Iterable containing keys to delete

        Returns: self

        Example:

            >>> from ww import d
            >>> current_dict = d({1: 1, 2: 2, 3: 3})
            >>> current_dict.delete(*[1,2])
            {3: 3}
        """
        for key in keys:
            self.pop(key, None)
        return self

    def clear(self):
        super(DictWrapper, self).clear()
        return self

    def copy(self):
        return self.__class__(self)

    def get(self, value, default=None):
        try:
            return self[value]
        except KeyError:
            return ensure_callable(default)()

    def setdefault(self, value, default=None):
        try:
            return self[value]
        except KeyError:
            self[value] = ensure_callable(default)()
            return self[value]

    def popitem(self, default=None):
        try:
            return dict.popitem(self)
        except KeyError:
            return ensure_callable(default)()

    def pp(self):
        return pprint(self)
