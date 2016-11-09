# coding: utf-8

# TODO: pretty print method

# TODO:
# foo = 1
# bar = 2
# d.from_vars('foo', 'bar')
# {'foo': 1, 'bar': 2}

import ww

from ww.types import Iterable, Hashable, Any  # noqa


class DictWrapper(dict):

    def isubset(self, *keys):
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
        return ww.g((key, self[key]) for key in keys)

    def subset(self, *keys):
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
        return self.__class__(self.isubset(*keys))

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

    def __iter__(self):
        """Return the inner iterator

        Returns: iterator

        """
        return iter(ww.g(self.items()))

    @classmethod
    def fromkeys(cls, iterable, value=None):
        # TODO : type: (Iterable, Union[Any, Callable]) -> DictWrapper
        # https://github.com/python/mypy/issues/2254
        """Create a new d from

        Args:
            iterable: Iterable containing keys
            value: value to associate with each key.
            If callable, will be value[key]

        Returns: new DictWrapper

        Example:

            >>> from ww import d
            >>> sorted(d.fromkeys('123', value=4).items())
            [('1', 4), ('2', 4), ('3', 4)]
            >>> sorted(d.fromkeys(range(3), value=lambda e:e**2).items())
            [(0, 0), (1, 1), (2, 4)]
        """
        if not callable(value):
            return cls(dict.fromkeys(iterable, value))

        return cls((key, value(key)) for key in iterable)

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
