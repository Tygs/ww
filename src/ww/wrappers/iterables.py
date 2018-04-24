# coding: utf-8

"""
    IterableWrapper is a convenient wrapper around all iterables.
    It works withs strings, lists, tuples, dicts, sets, file-like objects,
    anything declaring __len__ + __getitem__ or __next__, etc. Basically
    whatever you can apply a for loop to. And it will behave the same way
    regarding iteration.

    It does not assume a size, it does not even assumes the iterable is
    finite.

    When possible IterableWrapper tries to not hold data in memory, but some
    operations require it, so when in doubt, check the methods doc.

    However, remember that reading some iterables, such as generators,
    will consume them! Make sure this is what you want.

    In any case, IterableWrapper improves a lot over the API of regular
    iterable, providing better chaining, adding shorcuts to itertools,
    allowing slicing and more.

    .. WARNING::

        g() turns anything into a one-time chain of lazy generators. If you
        want to keep the underlying behavior of your iterable, g() is not the
        best choice. You can checkout l(), t(), s(), etc. for wrappers that
        match g() API but keep the behavior of the matchined data structure.

        However, g() has the advantage of working with ANY iterable, no matter
        the type or the size. Most of its methods are lazy and return a new
        instance of g().

        The other wrappers are specialized and try to mimic the behavior of
        one particular type: l() for lists, t() for tuples, s() for strings...

    Example:

        Import::

            >>> from ww import g

        You always have the more explicit import at your disposal::

            >>> from ww.wrappers.iterables import IterableWrapper

        `g` is just an alias of IterableWrapper, but it's what most people
        will want to use most of the time. Hence it's what we will use in the
        examples.

        `i` could have been a better alias for "iterable", but `i` is used
        all the time in Python as a variable name so it would systematically
        end up shadowed.`g` mnemonic is "generator".

        Basic usages::

            >>> from ww import g
            >>> gen = g(x * x for x in range(5))
            >>> gen
            <IterableWrapper generator>
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
            >>> gen.groupby(lambda x: x % 2).list() # autosort & cast groups
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

        .. WARNING::

            You can use indexing on g() like you would on list()


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
# TODO: support numpy slicing style
# TODO: support numpy filtering style
# TODO: get(item, default) that does try g[item] except IndexError: default
# https://docs.python.org/3/library/itertools.html#itertools-recipes
# TODO: safe_g

# WARNING: do not import unicode_literals, as it makes docstrings containing
# strings fail on python2
from __future__ import (absolute_import, division, print_function)

import random
import itertools

from collections import Iterator

from ww.types import (Any, Union, Callable, Iterable, T, T2, Generic,   # noqa
                      Iterator)

import builtins
from functools import reduce

import ww  # absolute import to avoid some circular references

from ww.tools.iterables import (at_index, iterslice, first_true, at_index_or,
                                chunks, window, firsts, lasts)
from ww.utils import ensure_tuple, _type_registry
from .base import BaseIterableWrapper

# todo : merge https://toolz.readthedocs.org/en/latest/api.html
# toto : merge https://github.com/kachayev/fn.py
# TODO: merge
# https://pythonhosted.org/natsort/natsort_keygen.html#natsort.natsort_keygen
# TODO: merge minibelt


@_type_registry('g')
class IterableWrapper(Iterator[T], BaseIterableWrapper, Generic[T]):

    def __init__(self, iterable, *more_iterables):
        # type: (Iterable, *Iterable) -> None
        """ Initialize self.iterator to iter(iterable)

            If several iterables are passed, they are concatenated.

            Args:
                iterable: iterable to use for the iner state.
                *more_iterables: other iterable to concatenate to the
                                 first one.

            Returns:
                None

            Raises:
                TypeError: if some arguments are not iterable.

            Example:

                >>> from ww import g
                >>> g(range(3)).list()
                [0, 1, 2]
                >>> g(range(3), "abc").list()
                [0, 1, 2, 'a', 'b', 'c']
        """

        # Check early if all elements are indeed iterables so that
        # they get an error now and not down the road while trying to
        # process it.
        for i, elem in enumerate((iterable, ) + more_iterables):
            try:
                iter(elem)
            except TypeError:
                raise TypeError(ww.s >> """
                    Argument "{}" of type "{}" (in position {}) is
                    not iterable. g() only accept iterables, meaning an object
                    you can use a for loop on. You can check if an object is
                    iterable by calling iter() on it (iterables don't raise
                    a TypeError). Also, iterables usually have either an
                    __iter__() method or a __len__() and __getitem__() method.
                """.format(elem, type(elem), i))

        self.iterator = iter(itertools.chain(iterable, *more_iterables))
        self._tee_called = False

    def __iter__(self):
        """ Return the inner iterator

            Example:

                >>> from ww import g
                >>> gen = g(range(10))
                >>> iter(gen) == gen.iterator
                True

            Returns:
                Inner iterator.

            Raises:
                RuntimeError: if trying call __iter__ after calling .tee()
        """
        if self._tee_called:
            raise RuntimeError("You can't iterate on a g object after g.tee "
                               "has been called on it.")
        return self.iterator

    # TODO: type self, and stuff that returns things depending on self
    def next(self, default=None):
        # type: (Any) -> Any
        """ Call next() on inner iterable.

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

    # alias for Python 2/3 compat
    __next__ = next

    def __add__(self, other):
        # type: (Iterable) -> IterableWrapper
        """ Return a generator that concatenates both generators.

            It uses itertools.chain(self, other_iterable), so it works when
            g() is on the left side of the addition.

            Args:
                other: The other iterable to chain with the current one.

            Returns:
                IterableWrapper

            Example:

                >>> from ww import g
                >>> (g(range(3)) + "abc").list()
                [0, 1, 2, 'a', 'b', 'c']
        """
        return self.__class__(itertools.chain(self.iterator, other))

    def __radd__(self, other):
        # type: (Iterable) -> IterableWrapper
        """ Return a generator that concatenates both iterable.

            It uses itertools.chain(other_iterable, self), so it works when
            g() is on the right side of the addition.

            Args:
                other: The other generator to chain with the current one.

            Example:

                >>> from ww import g
                >>> ("abc" + g(range(3))).list()
                ['a', 'b', 'c', 0, 1, 2]
        """
        return self.__class__(itertools.chain(other, self.iterator))

    # TODO: allow non iterables
    def __sub__(self, other):
        # type: (Iterable) -> IterableWrapper
        """ Yield items that are not in the other iterable.

            .. DANGER::
                The other iterable will be turned into a set. So make sure:

                - it has a finite size and can fit in memory.
                - you are ok with it being consumed if it's a generator.
                - it contains only hashable items.

            Args:
                other: The iterable to filter from.

            Example:

                >>> from ww import g
                >>> (g(range(6)) - [1, 2, 3]).list()
                [0, 4, 5]
        """
        filter_from = set(ensure_tuple(other))
        return self.__class__(x for x in self.iterator if x not in filter_from)

    # TODO: catch the exception when items are not hashable and raise
    # a better more explicit error
    def __rsub__(self, other):
        # type: (Iterable) -> IterableWrapper
        """ Yield items that are not in the other iterable.

            .. warning::
                The other iterable will be turned into a set. So make sure:

                - it has a finite size and can fit in memory.
                - you are ok with it being consumed if it's a generator.
                - it contains only hashable items.

            Args:
                other: The other generator to chain with the current one.

            Example:

                >>> from ww import g
                >>> (range(5) - g(range(3))).list()
                [3, 4]
        """
        filter_from = set(self.iterator)
        return self.__class__(x for x in other if x not in filter_from)

    def __mul__(self, num):
        # type: (int) -> IterableWrapper
        """ Duplicate itself and concatenate the results.

            It's basically a shortcut for `g().chain(*g().tee())`.

            Args:
                num: The number of times to duplicate.

            Example:

                >>> from ww import g
                >>> (g(range(3)) * 3).list()
                [0, 1, 2, 0, 1, 2, 0, 1, 2]
                >>> (2 * g(range(3))).list()
                [0, 1, 2, 0, 1, 2]
        """
        clones = itertools.tee(self.iterator, num)
        return self.__class__(itertools.chain(*clones))

    __rmul__ = __mul__

    def tee(self, num=2):
        # type: (int) -> IterableWrapper
        """ Return copies of this generator.

            Proxy to itertools.tee().

           If you want to concatenate the results afterwards, use
           g() * x instead of g().tee(x) which does that for you.

            Args:
                num: The number of returned generators.

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
        """ Act like [x] or [x:y:z] on a generator.

            .. WARNING::

                If you pass an index, it will return the element at this index
                as it would with any indexable. But it means that if your
                iterable is a generator, it WILL be consumed immidiatly up
                to that point.

                If you use a slice, it will return a generator and hence only
                consume your iterable once you start reading it.

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
            return first_true(self.iterator, index)

        try:
            start = index.start or 0
            step = index.step or 1
            stop = index.stop
        except AttributeError:
            raise ValueError('Indexing works only with integers or callables')

        return self.__class__(iterslice(self.iterator, start, stop, step))

    def map(self, callable):
        # type: (Callable) -> IterableWrapper
        """ Apply map() then wrap the result in g()

            Args:
                call: the callable to pass to map()

            Example:

                >>> from ww import g
                >>> g(range(3)).map(str).list()
                ['0', '1', '2']

        """
        return self.__class__(builtins.map(callable, self.iterator))

    def filter(self, callable):
        # type: (Callable) -> IterableWrapper
        """ Apply filter() then wrap the result in g()

            Args:
                call: the callable to pass to filter()

            Example:

                >>> from ww import g
                >>> g(range(3)).filter(bool).list()
                [1, 2]

        """
        return self.__class__(builtins.filter(callable, self.iterator))

    def reduce(self, callable, *args):
        # type: (Callable[..., T], Any) -> T
        """ Apply reduce() then wrap the result in g()

            Args:
                call: the callable to pass to reduce()

            Example:

                >>> from ww import g
                >>> g(range(3)).reduce(lambda a, b: a + b)
                3
                >>> g(range(3)).reduce(lambda a, b: a + b, 1)
                4
        """
        return reduce(callable, self.iterator, *args)

    def zip(self, *others):
        # type: (*Iterable) -> IterableWrapper
        """ Apply zip() then wrap in g()

            Args:
                others: the iterables to pass to zip()

            Example:

                >>> from ww import g
                >>> for element in g(range(3)).zip("abc"):
                ...     print(*element)
                0 a
                1 b
                2 c
                >>> for element in g(range(3)).zip("abc", [True, False, None]):
                ...    print(*element)
                0 a True
                1 b False
                2 c None
        """
        return self.__class__(builtins.zip(self.iterator, *others))

    # TODO: reduce

    # TODO: limit add an argument to limit the number of cycles.
    def cycle(self):
        # type: () -> IterableWrapper
        """ Create an infinite loop, chaining the iterable on itself

            Example:

                >>> from ww import g
                >>> gen = g(range(2)).cycle()
                >>> next(gen)
                0
                >>> next(gen)
                1
                >>> next(gen)
                0
                >>> next(gen)
                1
                >>> next(gen)
                0

            .. WARNING::

                Do not attempt a for loop on the result of cycle() unless
                you really know what you are doing. Cycle will loop
                forever. Remember you can slice g() objects.
        """
        return self.__class__(itertools.cycle(self.iterator))

    # TODO: provide the static method range(), and give it the habiility
    # to do itertools.count.
    def count(self):
        # type: () -> int
        """ Return the number of elements in the iterable.

            Example:

                >>> from ww import g
                >>> g(range(3)).count()
                3

        """
        try:
            return len(self.iterator)  # type: ignore
        except TypeError:
            for i, _ in enumerate(self.iterator, 1):
                pass
            return i

    def copy(self):
        # type: () -> IterableWrapper
        """ Return an exact copy of the iterable.

            The reference of the new iterable will be the same as the source
            when `copy()` was called.

            Example:

                >>> from ww import g
                >>> my_g_1 = g(range(3))
                >>> my_g_2 = my_g_1.copy()
                >>> next(my_g_1)
                0
                >>> next(my_g_1)
                1
                >>> next(my_g_2)
                0
        """

        self.iterator, new = itertools.tee(self.iterator)
        return self.__class__(new)

    def __repr__(self):
        # type: () -> str
        return "<IterableWrapper generator>"

    # TODO: use t() instead of tuple
    def chunks(self, size, cast=tuple):
        # type: (int, Callable) -> IterableWrapper
        """
            Yield items from an iterator in iterable chunks.

            Example:

            >>> from ww import g
            >>> my_g = g(range(12))
            >>> chunks = my_g.chunks(3)
            >>> print(chunks)
            <IterableWrapper generator>
            >>> chunks = chunks.list()
            >>> chunks[0]
            (0, 1, 2)
            >>> chunks[1]
            (3, 4, 5)
        """
        return self.__class__(chunks(self.iterator, size, cast))

    def window(self, size=2, cast=tuple):
        # type: (int, Callable) -> IterableWrapper
        """ Yield items using a sliding window.

            Wield chunks of a given size, but rolling only one item
            in and out at a time when iterating.

            Example:
                >>> from ww import g
                >>> my_g = g(range(12))
                >>> my_window = my_g.window(3).list()
                >>> my_window[0]
                (0, 1, 2)
                >>> my_window[1]
                (1, 2, 3)
        """
        return self.__class__(window(self.iterator, size, cast))

    def get(self, default=None):
        return at_index_or(self.iterator, default)

    def firsts(self, items=1, default=None):
        # type: (int, Any) -> IterableWrapper
        """ Lazily return the first x items from this iterable or default.

            Example:

            >>> from ww import g
            >>> my_g = g(range(12))
            >>> my_g.firsts(3).list()
            [0, 1, 2]
        """
        return self.__class__(firsts(self.iterator, items, default))

    def lasts(self, items=1, default=None):
        # type: (int, Any) -> IterableWrapper
        """ Lazily return the lasts x items from this iterable or default.

            Example:

            >>> from ww import g
            >>> my_g = g(range(12))
            >>> my_g.lasts(3).list()
            [9, 10, 11]

        """
        return self.__class__(lasts(self.iterator, items, default))

    # TODO: chance "default=None" to "No value" everywhere ?
    def sample(self, items=1, default=None, wrapper=ww.l):
        # TODO: put a warning to notify infinite size will break

        data = list(self.iterator)
        gap = len(data) - items
        if gap:
            data.extend(default for _ in range(gap))

        return wrapper(random.sample(data, items))

    def random(self, default=None):
        # TODO: put a warning to notify infinite size will break

        data = list(self.iterator)
        if not data:
            return default

        return random.choice(data)

    # TODO: add a consume() method
    def consume(self):
        any(self)
        return self

    def enumerate(self, start=0):
        # type: (int) -> IterableWrapper
        """ Give you the position of each element as you iterate.

            Args:
                start: the number to start counting from. Default is 0.

            Returns:
                An IterableWrapper, yielding (position, element)

            Example:

                >>> from ww import g
                >>> my_g = g('cheese')
                >>> my_g.enumerate().list()
                [(0, 'c'), (1, 'h'), (2, 'e'), (3, 'e'), (4, 's'), (5, 'e')]
                >>> g('cheese').enumerate(start=1).list()
                [(1, 'c'), (2, 'h'), (3, 'e'), (4, 'e'), (5, 's'), (6, 'e')]
        """
        return self.__class__(enumerate(self.iterator, start))
