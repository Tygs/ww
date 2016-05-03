
# TODO : make a s object for strings with split(regex|iterable), replace(regex|iterable)
# TODO : flags can be passed as strings. Ex: s.search('regex', flags='ig')
# TODO : make s.search(regex) return a wrapper with __bool__ evaluating to
# false if no match instead of None and allow default value for group(x)
# also allow match[1] to return group(1) and match['foo'] to return groupdict['foo']
# TODO .groups would be a g() object
# TODO stuff returning a strings in g() would be an s() object
# TODO s inherit from str
# TODO : add encoding detection, fuzzy_decode() to make the best of shitty decoding,
# unidecode, slug, etc,
# f() for format, if no args are passed, it uses local
# TODO: join() autocast to str, with a template you can customize
# TODO: match.__repr__ should show match, groups, groupsdict in summary
# TODO : if g() is called on a callable, iter() calls the callable everytime
# TODO: s.split(sep, maxsplit, minsize, default=None)
# so "a,b".split(',', minsize=2, default="b") == "a".split(',' minsize=2, default="b")
# TODO: g() + 1 apply the operation to the whole generator (as for *, / and -)
# TODO: g(x) + g(y) apply (a + b for a, b in zip(x, y))
# TODO : gen = gen(y); gen[gen > 5] has the same behavior as numpy array
# TODO: add features from https://docs.python.org/3/library/itertools.html#itertools-recipes
# TODO: allow s >> allow you to wrap a string AND dedent it automatically

from typing import Any, Union, Callable, Iterable

try:
    from itertools import (imap, izip, ifilter)
except ImportError:
    imap = map
    izip = zip
    ifilter = filter

from itertools import chain, tee, cycle

from .iterable import (at_index, iterslice, first_true, skip_duplicates,
                       chunks, window, groupby, first, last)
from .utils import ensure_tuple

# todo : merge https://toolz.readthedocs.org/en/latest/api.html
# toto : merge https://github.com/kachayev/fn.py
# TODO: merge https://pythonhosted.org/natsort/natsort_keygen.html#natsort.natsort_keygen


class g:

    def __init__(self, iterable: Iterable, *args: Iterable):
        """Initialize self.iterator to iter(iterable)

        If several iterables are passed, they are concatenated.

        Args:
            iterable: iterable to use for the iner state.
            *args: other iterable to concatenate to the first one.


        Example:

            >>> g(range(3)).list()
            [0, 1, 2]
            >>> g(range(3), "abc").list()
            [0, 1, 2, 'a', 'b', 'c']
        """

        if args:
            iterable = chain(iterable, *args)
        self.iterator = iter(iterable)
        self._tee_called = False

    def __iter__(self):
        """Return the inner iterable.

            Example:

            >>> gen = g(range(10))
            >>> iter(gen) == gen.iterable
            True
        """
        if self._tee_called:
            raise RuntimeError("You can't iterate on a g object after g.tee "
                               "has been called on it.")
        return self.iterator

    def next(self, default: Any=None):
        """Call next() on inner iterable.

        Args:
            default: default value to return if there is no next item
                     instead of raising StopIteration.

        Example:

            >>> g(range(10)).next()
            0
            >>> g(range(0)).next("foo")
            'foo'
        """
        return next(self.iterator, default)

    __next__ = next

    def __add__(self, other: Iterable):
        """Return a generator that concatenates both generators.

        It uses itertools.chain(self, other_iterable).

        Args:
            other: The other generator to chain with the current one.

        Example:

            >>> list(g(range(3)) + "abc")
            [0, 1, 2, 'a', 'b', 'c']
        """
        return g(chain(self.iterator, other))

    def __radd__(self, other: Iterable):
        """Return a generator that concatenates both generators.

        It uses itertools.chain(other_iterable, self).

        Args:
            other: The other generator to chain with the current one.

        Example:

            >>> list("abc" + g(range(3)))
            ['a', 'b', 'c', 0, 1, 2]
        """
        return g(chain(other, self.iterator))

    # TODO: allow non iterable
    def __sub__(self, other: Iterable):
        """Yield items that are not in the other iterable.

        The second iterable will be turned into a set so make sure:
            - it has a finite size and can fit in memory.
            - you are ok with it being consumed if it's a generator.
            - it contains only hashable items.


        Args:
            other: The iterable to filter from.

        Example:

            >>> list(g(range(6)) - [1, 2, 3])
            [0, 4, 5]
        """
        filter_from = set(ensure_tuple(other))
        return g(x for x in self if x not in filter_from)

    def __rsub__(self, other: Iterable):
        """Return a generator that concatenates both generators.

        It uses itertools.chain(other_iterable, self).

        Args:
            other: The other generator to chain with the current one.

        Example:

            >>> list("abc" + g(range(3)))
            ['a', 'b', 'c', 0, 1, 2]
        """
        filter_from = set(self.iterator)
        return g(x for x in other if x not in filter_from)

    def __mul__(self, num: int):
        """Duplicate itself and concatenate the results.

        Args:
            other: The number of times to duplicate.

        Example:

            >>> list(g(range(3)) * 3)
            [0, 1, 2, 0, 1, 2, 0, 1, 2]
            >>> list(2 * g(range(3)))
            [0, 1, 2, 0, 1, 2]
        """
        return g(chain(*tee(self.iterator, num)))

    __rmul__ = __mul__

    def tee(self, num: int=2):
        """Return copies of this generator.

        Proxy to itertools.tee().

        Args:
            other: The number of returned generators.

        Example:

            >>> list(tuple(x) for x in g(range(3)).clone(3))
            [(0, 1, 2), (0, 1, 2), (0, 1, 2)]
        """
        gen = g(g(x) for x in tee(self, num))
        self._tee_called = True
        return gen

    # TODO: allow negative end boundary
    def __getitem__(self, index: Union[int, slice]):
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
            ValueError: The step can not be negative: -1 given
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

        return g(iterslice(self.iterator, start, stop, step))

    def map(self, func: Callable):
        """Apply map() then wrap in g()

        Args:
            call: the callable to pass to map()

        Example:

            >>> g(range(3)).map(str).list()
            ['0', '1', '2']

        """
        return g(imap(func, self.iterator))

    def zip(self, *others: Iterable):
        """Apply zip() then wrap in g()

        Args:
            others: the iterables to pass to zip()

        """
        return g(izip(self.iterator, *others))

    def cycle(self):
        return g(cycle(self.iterator))

    def sorted(self, keyfunc=None, reverse=False):
        return g(sorted(self.iterator, key=reverse))

    def groupby(self, keyfunc=None, reverse=False, cast=tuple):
        return g(groupby(self, keyfunc, reverse, cast))

    def enumerate(self, start):
        return g(enumerate(self.iterator, start))

    def count(self):
        try:
            return len(self.iterator)
        except TypeError:
            for i, _ in enumerate(self.iterator):
                pass
            return i

    def copy(self):
        self.iterator, new = tee(self.iterator)
        return g(new)

    def list(self):
        return list(self.iterator)

    def tuple(self):
        return tuple(self.iterator)

    def set(self):
        return set(self.iterator)

    def join(self, separator="", cast=str):
        return separator.join(cast(x) for x in self.iterator)

    def __repr__(self):
        return "<g generator>"

    def chunks(self, chunksize, cast=__builtins__['tuple']):
        """
            Yields items from an iterator in iterable chunks.
        """
        return g(chunks(self.iterator, chunksize, cast))

    def window(self, size=2, cast=__builtins__['tuple']):
        """
        Yields iterms by bunch of a given size, but rolling only one item
        in and out at a time when iterating.
        """
        return g(window(self.iterator, size, cast))

    def first(self, items=1, default=None):
        return g(first(self.iterator, items, default))

    def last(self, items=1, default=None):
        return g(last(self.iterator, items, default))

    # allow using a bloom filter as an alternative to set
    # https://github.com/jaybaird/python-bloomfilter
    def skip_duplicates(self, key=lambda x: x,  fingerprints=None):
        return g(skip_duplicates(self.iterator, key, fingerprints))
