# coding: utf-8

"""
    IterableWrapper is a convenient wrapper around all iterables.
    It works withs strings, lists, tuples, dicts, sets, file-like objects,
    anything declaring __len__ + __getitem__ or __next__, etc. Basically
    whatever you can apply a for loop to. And it will behave the same way
    regarding iteration.

    It does not assume a size, it does not even assumes the iterable is finite.

    When possible IterableWrapper tries to not hold data in memory, but some
    operations require it, so when in doubt, check the methods doc.

    However, remember that reading some iterables, such as generators,
    will consume them! Make sure this is what you want.

    In any case, IterableWrapper improves a lot over the API of regular
    iterable, providing better chaining, adding shorcuts to itertools,
    allowing slicing and more.

    Example:

        Import::

            >>> from ww import g

        You always have the more explicit import at your disposal::

            >>> from ww.wrappers.iterables import IterableWrapper

        `g` is just an alias of IterableWrapper, but it's what most people will
        want to use most of the time. Hence it's what we will use in the
        examples.

        `i` could have been a better alias for "iterable", but `i` is used
        all the time in Python as a variable name so it would systematically
        end up shadowed.`g` mnemonic is "generator".

        Basic usages::

            >>> from ww import g
            >>> gen = g(x * x for x in range(5))
            >>> gen
            <IterableWrapper generator>
            >>> type(gen)
            <class 'ww.wrappers.iterables.IterableWrapper'>
            >>> for x in gen: # you can iterate on g as expected
            ...     print(x)
            ...
            0
            1
            4
            9
            16

        Shortcuts and chaining::

            >>> g("azerty").enumerate().sorted().list()
            [(0, 'a'), (1, 'z'), (2, 'e'), (3, 'r'), (4, 't'), (5, 'y')]
            >>> g(range(3)).join(',') # natural join, with autocast to string
            u'0,1,2'

        Itertools at your fingertips::

            >>> gen = g(x * x for x in range(10))
            >>> gen.groupby(lambda x: x % 2).list() # autosort and cast groups
            [(0, (0, 4, 16, 36, 64)), (1, (1, 9, 25, 49, 81))]
            >>> a, b = g(range(3)).tee(2)
            >>> a.list()
            [0, 1, 2]
            >>> b.list()
            [0, 1, 2]
            >>> gen = g(range(2)).cycle()
            >>> next(gen)
            0
            >>> next(gen)
            1
            >>> next(gen)
            0
            >>> next(gen)
            1

        Operators to the rescue:

            >>> gen = g(range(3)) + "abc"
            >>> gen.list()
            [0, 1, 2, 'a', 'b', 'c']
            >>> gen = g(range(5)) - [0, 3]
            >>> gen.list()
            [1, 2, 4]
            >>> gen = g(range(3)) * 3
            >>> gen.list()
            [0, 1, 2, 0, 1, 2, 0, 1, 2]

        Index all the things!!!

        ::

            >>> gen = g(x * x for x in range(10))
            >>> gen[3:8].list() # slicing uses itertools.islice
            [9, 16, 25, 36, 49]
            >>> gen = g(x * x for x in range(10))
            >>> gen[3]
            9
            >>> # slicing with a callable will start/stop when first True
            >>> g('aeRty')[lambda x: x.isupper():].list()
            ['R', 't', 'y']

        Moar features::

            >>> a, b, c = g(range(1)).firsts(3, default="foo")
            >>> a
            0
            >>> b
            'foo'
            >>> c
            'foo'
            >>> g(range(10)).chunks(3).list()
            [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]
            >>> # preserve order, works on unsized containers, has a key func
            >>> g("azertyazertyazerty").skip_duplicates().list()
            ['a', 'z', 'e', 'r', 't', 'y']

    There is much, much more...

    Plus, most feature from this module are actually just delegating the work
    to the ww.tools.iterable module. It contains stand alone functions for
    most operations you can apply directly on regular collections.

    You may want to use it directly if you wish to not wrap your collections
    in g().

    You'll find bellow the detailed documentation for each method of
    IterableWrapper. Go have a look, there is some great stuff here!
"""

# TODO stuff returning a strings in g() would be an s() object
# TODO: add features from
# TODO: get(item, default) that does try g[item] except IndexError: default
# https://docs.python.org/3/library/itertools.html#itertools-recipes

# WARNING: do not import unicode_literals, as it makes docstrings containins
# strings fail on python2
from __future__ import (absolute_import, division, print_function)

import itertools

try:  # Python 2 doesn't have those imports
    from typing import Any, Union, Callable, Iterable  # noqa
except ImportError:
    pass

try:  # Aliases for Python 2
    from itertools import imap, izip, ifilter  # type: ignore noqa
except ImportError:
    imap = map
    izip = zip
    ifilter = filter

import builtins

import ww  # absolute import to avoid some circular references

from ww.tools.iterables import (at_index, iterslice, first_true,
                                skip_duplicates, chunks, window, firsts, lasts)
from ww.utils import ensure_tuple
from .base import BaseWrapper

# todo : merge https://toolz.readthedocs.org/en/latest/api.html
# toto : merge https://github.com/kachayev/fn.py
# TODO: merge
# https://pythonhosted.org/natsort/natsort_keygen.html#natsort.natsort_keygen
# TODO: merge minibelt


class IterableWrapper(BaseWrapper):

    def __init__(self, iterable, *args):
        # type: (Iterable, *Iterable) -> None
        """Initialize self.iterator to iter(iterable)

        If several iterables are passed, they are concatenated.

        Args:
            iterable: iterable to use for the iner state.
            *args: other iterable to concatenate to the first one.

        Example:

            >>> from ww import g
            >>> g(range(3)).list()
            [0, 1, 2]
            >>> g(range(3), "abc").list()
            [0, 1, 2, 'a', 'b', 'c']
        """

        if args:
            iterable = itertools.chain(iterable, *args)
        self.iterator = iter(iterable)
        self._tee_called = False

    def __iter__(self):
        """Return the inner iterator

            Example:

            >>> from ww import g
            >>> gen = g(range(10))
            >>> iter(gen) == gen.iterator
            True
        """
        if self._tee_called:
            raise RuntimeError("You can't iterate on a g object after g.tee "
                               "has been called on it.")
        return self.iterator

    def next(self, default=None):
        # type: (Any) -> Any
        """Call next() on inner iterable.

        Args:
            default: default value to return if there is no next item
                     instead of raising StopIteration.

        Example:

            >>> from ww import g
            >>> g(range(10)).next()
            0
            >>> g(range(0)).next("foo")
            'foo'
        """
        return next(self.iterator, default)

    __next__ = next

    def __add__(self, other):
        # type: (Iterable) -> IterableWrapper
        """Return a generator that concatenates both generators.

        It uses itertools.chain(self, other_iterable).

        Args:
            other: The other generator to chain with the current one.

        Example:

            >>> from ww import g
            >>> list(g(range(3)) + "abc")
            [0, 1, 2, 'a', 'b', 'c']
        """
        return self.__class__(itertools.chain(self.iterator, other))

    def __radd__(self, other):
        # type: (Iterable) -> IterableWrapper
        """Return a generator that concatenates both generators.

        It uses itertools.chain(other_iterable, self).

        Args:
            other: The other generator to chain with the current one.

        Example:

            >>> from ww import g
            >>> list("abc" + g(range(3)))
            ['a', 'b', 'c', 0, 1, 2]
        """
        return self.__class__(itertools.chain(other, self.iterator))

    # TODO: allow non iterables
    def __sub__(self, other):
        # type: (Iterable) -> IterableWrapper
        """Yield items that are not in the other iterable.

        The second iterable will be turned into a set so make sure:
            - it has a finite size and can fit in memory.
            - you are ok with it being consumed if it's a generator.
            - it contains only hashable items.

        Args:
            other: The iterable to filter from.

        Example:

            >>> from ww import g
            >>> list(g(range(6)) - [1, 2, 3])
            [0, 4, 5]
        """
        filter_from = set(ensure_tuple(other))
        return self.__class__(x for x in self.iterator if x not in filter_from)

    def __rsub__(self, other):
        # type: (Iterable) -> IterableWrapper
        """Return a generator that concatenates both generators.

        It uses itertools.chain(other_iterable, self).

        Args:
            other: The other generator to chain with the current one.

        Example:

            >>> from ww import g
            >>> list("abc" + g(range(3)))
            ['a', 'b', 'c', 0, 1, 2]
        """
        filter_from = set(self.iterator)
        return self.__class__(x for x in other if x not in filter_from)

    def __mul__(self, num):
        # type: (int) -> IterableWrapper
        """Duplicate itself and concatenate the results.

        Args:
            other: The number of times to duplicate.

        Example:

            >>> from ww import g
            >>> list(g(range(3)) * 3)
            [0, 1, 2, 0, 1, 2, 0, 1, 2]
            >>> list(2 * g(range(3)))
            [0, 1, 2, 0, 1, 2]
        """
        clones = itertools.tee(self.iterator, num)
        return self.__class__(itertools.chain(*clones))

    __rmul__ = __mul__

    def tee(self, num=2):
        # type: (int) -> IterableWrapper
        """Return copies of this generator.

        Proxy to itertools.tee().

        Args:
            other: The number of returned generators.

        Example:

            >>> from ww import g
            >>> a, b, c = g(range(3)).tee(3)
            >>> [tuple(a), tuple(b), tuple(c)]
            [(0, 1, 2), (0, 1, 2), (0, 1, 2)]
        """
        cls = self.__class__
        gen = cls(cls(x) for x in itertools.tee(self.iterator, num))
        self._tee_called = True
        return gen

    # TODO: allow negative end boundary
    def __getitem__(self, index):
        # type: (Union[int, slice, Callable]) -> Union[IterableWrapper, Any]
        """Act like [x] or [x:y:z] on a generator. Warnings apply.

        If you use an index instead of slice, you should know it WILL
        consume the generator up to this index.

        If you use a slice, it will return a generator.

        If you want to keep the behavior of the underlying data structure,
        don't use g(). Do it the usual way. g() will turn anything into a
        one-time generator.

        Args:
            index: the index of the item to return, or a slice to apply to
                   the iterable.

        Raises:
            IndexError: if the index is bigger than the iterable size.

        Example:

            >>> from ww import g
            >>> g(range(3))[1]
            1
            >>> g(range(3))[4]
            Traceback (most recent call last):
            ...
            IndexError: Index "4" out of range
            >>> g(range(100))[3:10].list()
            [3, 4, 5, 6, 7, 8, 9]
            >>> g(range(100))[3:].list() # doctest: +ELLIPSIS
            [3, 4, 5, 6, 7, 8, 9, ..., 99]
            >>> g(range(100))[:10].list()
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            >>> g(range(100))[::2].list()
            [0, 2, 4, ..., 96, 98]
            >>> g(range(100))[::-1]
            Traceback (most recent call last):
            ...
            ValueError: The step can not be negative: '-1' given
        """

        if isinstance(index, int):
            return at_index(self.iterator, index)

        if callable(index):
            return first_true(self.iterator, index)  # type: ignore

        try:
            start = index.start or 0  # type: ignore
            step = index.step or 1  # type: ignore
            stop = index.stop  # type: ignore
        except AttributeError:
            raise ValueError('Indexing works only with integers or callables')

        return self.__class__(iterslice(self.iterator, start, stop, step))

    def map(self, func):
        # type: (Callable) -> IterableWrapper
        """Apply map() then wrap in g()

        Args:
            call: the callable to pass to map()

        Example:

            >>> from ww import g
            >>> g(range(3)).map(str).list()
            ['0', '1', '2']

        """
        return self.__class__(imap(func, self.iterator))

    def zip(self, *others):
        # type: (*Iterable) -> IterableWrapper
        """Apply zip() then wrap in g()

        Args:
            others: the iterables to pass to zip()

        """
        return self.__class__(izip(self.iterator, *others))

    def cycle(self):
        return self.__class__(itertools.cycle(self.iterator))

    def sorted(self, keyfunc=None, reverse=False):
        # type: (Callable, bool) -> IterableWrapper
        # using builtins to avoid shadowing
        lst = builtins.sorted(self.iterator, key=keyfunc, reverse=reverse)
        return self.__class__(lst)

    def groupby(self, keyfunc=None, reverse=False, cast=tuple):
        # type: (Callable, bool, Callable) -> IterableWrapper
        # full name to avoid shadowing
        gen = ww.tools.iterables.groupby(self.iterator, keyfunc, reverse, cast)
        return self.__class__(gen)

    def enumerate(self, start=0):
        # type: (int) -> IterableWrapper
        return self.__class__(enumerate(self.iterator, start))

    def count(self):
        try:
            return len(self.iterator)
        except TypeError:
            for i, _ in enumerate(self.iterator):
                pass
            return i

    def copy(self):
        self.iterator, new = itertools.tee(self.iterator)
        return self.__class__(new)

    def join(self, joiner, formatter=lambda s, t: t.format(s), template="{}"):
        # type: (Iterable, Callable, str) -> ww.s.StringWrapper
        return ww.s(joiner).join(self, formatter, template)

    def __repr__(self):
        return "<IterableWrapper generator>"

    # TODO: use t() instead of tuple
    def chunks(self, chunksize, cast=tuple):
        # type: (int, Callable) -> IterableWrapper
        """
            Yields items from an iterator in iterable chunks.
        """
        return self.__class__(chunks(self.iterator, chunksize, cast))

    def window(self, size=2, cast=tuple):
        # type: (int, Callable) -> IterableWrapper
        """
        Yields iterms by bunch of a given size, but rolling only one item
        in and out at a time when iterating.
        """
        return self.__class__(window(self.iterator, size, cast))

    def firsts(self, items=1, default=None):
        # type: (int, Any) -> IterableWrapper
        """ Lazily return the first x items from this iterable or default. """
        return self.__class__(firsts(self.iterator, items, default))

    def lasts(self, items=1, default=None):
        # type: (int, Any) -> IterableWrapper
        """ Lazily return the lasts x items from this iterable or default. """
        return self.__class__(lasts(self.iterator, items, default))

    # allow using a bloom filter as an alternative to set
    # https://github.com/jaybaird/python-bloomfilter
    # TODO : find a way to say "any type accepting 'in'"
    def skip_duplicates(self, key=lambda x: x, fingerprints=None):
        # type: (Callable, Any) -> IterableWrapper
        uniques = skip_duplicates(self.iterator, key, fingerprints)
        return self.__class__(uniques)
