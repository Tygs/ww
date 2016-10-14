# TODO: delete(keys)


class DictWrapper(dict):
    def isubset(self, *keys):
        """Return key, self[key] as generator for key in keys.

        Raise KeyError if a key does not exist

        Args:
            keys: Iterable containing keys

        Example:

            >>> list(d({1:1, 2:2, 3:3}).isubset(1,3))
            [(1, 1), (3, 3)]
        """
        for key in keys:
            yield key, self[key]

    def subset(self, *keys):
        """Return d(key, self[key]) for key in keys.

        Raise KeyError if a key does not exist

        Args:
            keys: Iterable containing keys

        Example:

            >>> d({1:1, 2:2, 3:3}).subset(1,3)
            {1: 1, 3: 3}
        """
        return d(self.isubset(*keys))

    def swap(self):
        """Swap key and value

        /!\ Be carreful, if there are duplicate values, only one will
        survive /!\

        Example:

            >>> d({1:2, 2:2, 3:3}).swap()
            {2: 2, 3: 3}
        """
        return d((v, k) for k, v in self.items())

    def add(self, key, value):
        """Add value in key

        Args:
            key: Key
            value: Value to associate to the key

        Example:

            >>> current_dict = d({1:1, 2:2, 3:3})
            >>> current_dict.add(4,5)
            {1: 1, 2: 2, 3: 3, 4: 5}
        """
        self[key] = value
        return self

    def __iter__(self):
        for key, value in self.items():
            yield key, value

    @classmethod
    def fromkeys(cls, *keys, **kwargs):
        """Create a new d from

        Args:
            *keys: Iterable containing keys

        Returns: d

        Example:

            >>> sorted(d.fromkeys(*'123', value=4).items())
            [('1', 4), ('2', 4), ('3', 4)]
        """
        value = kwargs.get('value', None)
        if not callable(value):
            return d(super(d, cls).fromkeys(keys, value))

        def gen():
            for key in keys:
                yield key, value(key)

        return d(gen())

    def merge(self, other_dict):
        """Merge self with other_dict

        Args:
            other_dict: dict to merge with self

        Returns: merged dict

        Example:

            >>> current_dict = d({1:1, 2:2, 3:3})
            >>> to_merge_dict = d({3:4, 4:5})
            >>> current_dict.merge(to_merge_dict)
            {1: 1, 2: 2, 3: 4, 4: 5}
        """
        self.update(other_dict)
        return self

    def delete(self, *keys):
        """Delete keys from dict

        Args:
            *keys: Iterable containing keys to delete

        Returns: self

        Example:

            >>> current_dict = d({1:1, 2:2, 3:3})
            >>> current_dict.delete(*[1,2])
            {3: 3}
        """
        for key in keys:
            self.pop(key, None)
        return self

    def __add__(self, other):
        """Add other in self and return new dict

        Args:
            other: dict to add in self

        Returns: Merged dict

        Example:

            >>> current_dict = d({1:1, 2:2, 3:3})
            >>> to_merge_dict = {3:4, 4:5}
            >>> current_dict + to_merge_dict
            {1: 1, 2: 2, 3: 4, 4: 5}
        """
        copy = d(self.copy())
        return copy.merge(other)

    def __radd__(self, other):
        """Add other in self, and return new dict

        Args:
            other: dict to add in self

        Returns: Merged dict

        Example:

            >>> current_dict = {1:1, 2:2, 3:3}
            >>> to_merge_dict = d({3:4, 4:5})
            >>> current_dict + to_merge_dict
            {1: 1, 2: 2, 3: 4, 4: 5}
        """
        copy = d(other.copy())
        return copy.merge(self)


    def __iadd__(self, other):
        """Add other in self

        Args:
            other: Dict to add in self

        Returns: Merded dict

        Example:

            >>> current_dict = d({1: 1, 2: 2, 3: 3})
            >>> current_dict += {5: 6, 6: 7}
            {1: 1, 2: 2, 3: 3, 5: 6, 6: 7}
        """
        return self.merge(other)

d=DictWrapper
