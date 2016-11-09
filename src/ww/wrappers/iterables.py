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

# WARNING: do not import unicode_literals, as it makes docstrings containing
# strings fail on python2
from __future__ import (absolute_import, division, print_function)

import itertools

from collections import Iterable as IterableAbc, Iterator

from ww.types import Any, Union, Callable, Iterable, T, T2  # noqa
from ww.utils import renamed_argument

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


class IterableWrapper(Iterator, IterableAbc, BaseWrapper):

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
            return first_true(self.iterator, index)  # type: ignore

        try:
            start = index.start or 0  # type: ignore
            step = index.step or 1  # type: ignore
            stop = index.stop  # type: ignore
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

    # TODO: add filter so we can do the filter(bool) trick

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

    @renamed_argument('key', 'keyfunc')
    def sorted(self, keyfunc=None, reverse=False):
        # type: (Callable, bool) -> IterableWrapper
        """ Sort the iterable.

            .. warning::

                This will load the entire iterable in memory. Remember you
                can slice g() objects before you sort them. Also remember you
                can use callable in g() object slices, making it easy to start
                or stop iteration on a condition.

            Args:
                keyfunc: A callable that must accept the current element to
                         sort and return the object used to determine it's
                         position. Default to return the object itselt.
                reverse: If True, the iterable is sorted in the descending
                         order instead of ascending. Default is False.

            Returns:
                The sorted iterable.

            Example:

                >>> from ww import g
                >>> animals = ['dog', 'cat', 'zebra', 'monkey']
                >>> for animal in g(animals).sorted():
                ...     print(animal)
                cat
                dog
                monkey
                zebra
                >>> for animal in g(animals).sorted(reverse=True):
                ...     print(animal)
                zebra
                monkey
                dog
                cat
                >>> for animal in g(animals).sorted(lambda animal: animal[-1]):
                ...     print(animal)
                zebra
                dog
                cat
                monkey
        """
        # using builtins to avoid shadowing
        lst = builtins.sorted(self.iterator, key=keyfunc, reverse=reverse)
        return self.__class__(lst)

    # TODO: add a sort_func argument to allow to choose the sorting strategy
    # and remove the reverse argument
    def groupby(self,
                keyfunc=None,  # type: Callable[T]
                reverse=False,  # type: bool
                cast=tuple  # type: Callable[T2]
                ):  # type: (...) -> IterableWrapper
        """ Group items according to one common feature.

            Create a generator yielding (group, grouped_items) pairs, with
            "group" being the return value of `keyfunc`, and grouped_items
            being an iterable of items maching this group.

            Unlike itertools.groupy, the iterable is automatically sorted for
            you, also using the `keyfunc`, since this is what you mostly want
            to do anyway and forgetting to sort leads to useless results.

            Args:
                keyfunc: A callable that must accept the current element to
                         group and return the object you wish to use
                         to determine in which group the element belongs to.
                         This object will also be used for the sorting.
                reverse: If True, the iterable is sorted in the descending
                         order instead of ascending. Default is False.
                         You probably don't need to use this, we provide it
                         just in case there is an edge case we didn't think
                         about.
                cast: A callable used to choose the type of the groups of
                      items. The default is to return items grouped as a tuple.
                      If you want groups to be generators, pass an identity
                      function such as lambda x: x.

            Returns:
                An IterableWrapper, yielding (group, grouped_items)

            Example:

                >>> from ww import g
                >>> my_gen = g(['morbier', 'cheddar', 'cantal', 'munster'])
                >>> my_gen.groupby(lambda i: i[0]).list()
                [('c', ('cheddar', 'cantal')), ('m', ('morbier', 'munster'))]
                >>> my_gen = g(['morbier', 'cheddar', 'cantal', 'munster'])
                >>> my_gen.groupby(len, cast=list).list()
                [(6, ['cantal']), (7, ['morbier', 'cheddar', 'munster'])]

        """
        # full name to avoid shadowing
        gen = ww.tools.iterables.groupby(self.iterator, keyfunc, reverse, cast)
        return self.__class__(gen)

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

    def join(self, joiner, formatter=lambda s, t: t.format(s), template="{}"):
        # type: (str, Callable, str) -> ww.s.StringWrapper
        """ Join every item of the iterable into a string.
            This is just like the `join()` method on `str()`, but conveniently
            stored on the iterable itself.

            Example:

                >>> from ww import g
                >>> g(range(3)).join('|')
                u'0|1|2'
                >>> to_string = lambda s, t: str(s) * s
                >>> print(g(range(1, 4)).join(',', formatter=to_string))
                1,22,333
                >>> print(g(range(3)).join('\\n', template='- {}'))
                - 0
                - 1
                - 2
        """
        return ww.s(joiner).join(self, formatter, template)

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
            >>> print(type(chunks))
            <class 'ww.wrappers.iterables.IterableWrapper'>
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

    # allow using a bloom filter as an alternative to set
    # https://github.com/jaybaird/python-bloomfilter
    # TODO : find a way to say "any type accepting 'in'"
    def skip_duplicates(self, key=lambda x: x, fingerprints=None):
        # type: (Callable, Any) -> IterableWrapper
        """ Yield unique values.

            Returns a generator that will yield all objects from iterable,
            skipping duplicates.

            Duplicates are identified using the `key` function to calculate a
            unique fingerprint. This does not use natural equality, but the
            result use a set() to remove duplicates, so defining __eq__
            on your objects would have no effect.

            By default the fingerprint is the object itself, which ensure the
            functions works as-is with an iterable of primitives such as int,
            str or tuple.

            :Example:

                >>> list(skip_duplicates([1, 2, 3, 4, 4, 2, 1, 3 , 4]))
                [1, 2, 3, 4]

            The return value of `key` MUST be hashable, which means for
            non hashable objects such as dict, set or list, you need to specify
            a function that returns a hashable fingerprint.

            :Example:

                >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)),
                ...                      lambda x: tuple(x)))
                [[], [1, 2]]
                >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)),
                ...                      lambda x: (type(x), tuple(x))))
                [[], (), [1, 2], (1, 2)]

            For more complex types, such as custom classes, the default
            behavior is to remove nothing. You MUST provide a `key` function is
            you wish to filter those.

            :Example:

                >>> class Test(object):
                ...    def __init__(self, foo='bar'):
                ...        self.foo = foo
                ...    def __repr__(self):
                ...        return "Test('%s')" % self.foo
                ...
                >>> list(skip_duplicates([Test(), Test(), Test('other')]))
                [Test('bar'), Test('bar'), Test('other')]
                >>> list(skip_duplicates([Test(), Test(), Test('other')],\
                                         lambda x: x.foo))
                [Test('bar'), Test('other')]

        """

        uniques = skip_duplicates(self.iterator, key, fingerprints)
        return self.__class__(uniques)

    # TODO: add a consume() method
