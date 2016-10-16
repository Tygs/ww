# coding: utf-8

import itertools

from future.utils import raise_from

try:
    from typing import Union, Callable, Iterable, Any, TypeVar   # noqa
    T = TypeVar('T')
except ImportError:
    pass

from collections import deque


def starts_when(iterable, condition):
    # type: (Iterable, Union[Callable, Any]) -> Iterable
    """Start yielding items when a condition arise.

    Args:
        condition: if the callable returns True once, start yielding
                   items. If it's not a callable, it will be converted
                   to one as `lambda condition: condition == item`.

    Example:

        >>> list(starts_when(range(10), lambda x: x > 5))
        [6, 7, 8, 9]
        >>> list(starts_when(range(10), 7))
        [7, 8, 9]
    """
    if not callable(condition):
        cond_value = condition

        def condition(x):
            return x == cond_value
    return itertools.dropwhile(lambda x: not condition(x), iterable)


def stops_when(iterable, condition):
    # type: (Iterable, Union[Callable, Any]) -> Iterable
    """Stop yielding items when a condition arise.

    Args:
        condition: if the callable returns True once, stop yielding
                   items. If it's not a callable, it will be converted
                   to one as `lambda condition: condition == item`.

    Example:

        >>> list(stops_when(range(10), lambda x: x > 5))
        [0, 1, 2, 3, 4, 5]
        >>> list(stops_when(range(10), 7))
        [0, 1, 2, 3, 4, 5, 6]
    """
    if not callable(condition):
        cond_value = condition

        def condition(x):
            return x == cond_value
    return itertools.takewhile(lambda x: not condition(x), iterable)


def skip_duplicates(iterable, key=None, fingerprints=()):
    # type: (Iterable, Callable, Any) -> Iterable
    """
        Returns a generator that will yield all objects from iterable, skipping
        duplicates.

        Duplicates are identified using the `key` function to calculate a
        unique fingerprint. This does not use natural equality, but the
        result use a set() to remove duplicates, so defining __eq__
        on your objects would have no effect.

        By default the fingerprint is the object itself,
        which ensure the functions works as-is with an iterable of primitives
        such as int, str or tuple.

        :Example:

            >>> list(skip_duplicates([1, 2, 3, 4, 4, 2, 1, 3 , 4]))
            [1, 2, 3, 4]

        The return value of `key` MUST be hashable, which means for
        non hashable objects such as dict, set or list, you need to specify
        a a function that returns a hashable fingerprint.

        :Example:

            >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)),
            ...                      lambda x: tuple(x)))
            [[], [1, 2]]
            >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)),
            ...                      lambda x: (type(x), tuple(x))))
            [[], (), [1, 2], (1, 2)]

        For more complex types, such as custom classes, the default behavior
        is to remove nothing. You MUST provide a `key` function is you wish
        to filter those.

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

    fingerprints = fingerprints or set()

    try:
        # duplicate some code to gain perf in the most common case
        if key is None:
            for x in iterable:
                if x not in fingerprints:
                    yield x
                    fingerprints.add(x)
        else:
            for x in iterable:
                fingerprint = key(x)
                if fingerprint not in fingerprints:
                    yield x
                    fingerprints.add(fingerprint)
    except TypeError:
        try:
            hash(fingerprint)
        except TypeError:
            raise TypeError(
                "The 'key' function returned a non hashable object of type "
                "'%s' when receiving '%s'. Make sure this function always "
                "returns a hashable object. Hint: immutable primitives like"
                "int, str or tuple, are hashable while dict, set and list are "
                "not." % (type(fingerprint), x))
        else:
            raise


# TODO: test that on big iterators to check for recursion limit
def chunks(iterable, chunksize, cast=tuple):
    # type: (Iterable, int, Callable) -> Iterable
    """
        Yields items from an iterator in iterable chunks.
    """
    it = iter(iterable)
    while True:
        yield cast(itertools.chain([next(it)],
                   itertools.islice(it, chunksize - 1)))


def window(iterable, size=2, cast=tuple):
    # type: (Iterable, int, Callable) -> Iterable
    """
        Yields iterms by bunch of a given size, but rolling only one item
        in and out at a time when iterating.

        >>> list(window([1, 2, 3]))
        [(1, 2), (2, 3)]

        By default, this will cast the window to a tuple before yielding it;
        however, any function that will accept an iterable as its argument
        is a valid target.

        If you pass None as a cast value, the deque will be returned as-is,
        which is more performant. However, since only one deque is used
        for the entire iteration, you'll get the same reference everytime,
        only the deque will contains different items. The result might not
        be what you want :

        >>> list(window([1, 2, 3], cast=None))
        [deque([2, 3], maxlen=2), deque([2, 3], maxlen=2)]

    """
    iterable = iter(iterable)
    d = deque(itertools.islice(iterable, size), size)
    if cast:
        yield cast(d)
        for x in iterable:
            d.append(x)
            yield cast(d)
    else:
        yield d
        for x in iterable:
            d.append(x)
            yield d


def at_index(iterable, index):
    # type: (Iterable[T], int) -> T
    """" Return the item at the index of this iterable or raises IndexError.

        WARNING: this will consume generators.

        Negative indices are allowed but be aware they will cause n items to
        be held in memory, where n = abs(index)
    """
    try:
        if index < 0:
            return deque(iterable, maxlen=abs(index)).popleft()

        return next(itertools.islice(iterable, index, index + 1))
    except (StopIteration, IndexError) as e:
        raise_from(IndexError('Index "%d" out of range' % index), e)


def first_true(iterable, func):
    # type: (Iterable[T], Callable) -> T
    """" Return the first item of the iterable for which func(item) == True.

        Or raises IndexError.

        WARNING: this will consume generators.
    """
    try:
        return next((x for x in iterable if func(x)))
    except StopIteration as e:
        raise_from(IndexError('No match for %s' % func), e)


def iterslice(iterable, start=0, stop=None, step=1):
    # type: (Iterable[T], int, int, int) -> Iterable[T]
    """ Like itertools.islice, but accept int and callables.

        If `start` is a callable, start the slice after the first time
        start(item) == True.

        If `stop` is a callable, stop the slice after the first time
        stop(item) == True.
    """

    if step < 0:
        raise ValueError("The step can not be negative: '%s' given" % step)

    if not isinstance(start, int):

        # [Callable:Callable]
        if not isinstance(stop, int) and stop:
            return stops_when(starts_when(iterable, start), stop)

        # [Callable:int]
        return starts_when(itertools.islice(iterable, None, stop, step), start)

    # [int:Callable]
    if not isinstance(stop, int) and stop:
        return stops_when(itertools.islice(iterable, start, None, step), stop)

    # [int:int]
    return itertools.islice(iterable, start, stop, step)


def groupby(iterable, keyfunc=None, reverse=False, cast=tuple):
    # type: (Iterable, Callable, bool, Callable) -> Iterable
    sorted_iterable = sorted(iterable, key=keyfunc, reverse=reverse)
    for key, group in itertools.groupby(sorted_iterable, keyfunc):
        yield key, cast(group)


def firsts(iterable, items=1, default=None):
    # type: (Iterable[T], int, T) -> Iterable[T]
    """ Lazily return the first x items from this iterable or default. """

    try:
        items = int(items)
        assert items >= 0
    except (TypeError, AssertionError):
        raise ValueError("items should be set so that int(items) >= 0")

    for i, item in zip(range(items), iterable):
        yield item

    for x in range(items - (i + 1)):
        yield default


def lasts(iterable, items=1, default=None):
    # type: (Iterable[T], int, T) -> Iterable[T]
    """ Lazily return the last x items from this iterable or default. """

    last_items = deque(iterable, maxlen=items)

    for x in range(items - len(last_items)):
        yield default

    for y in last_items:
        yield y
