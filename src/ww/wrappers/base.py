# coding: utf-8

from pprint import pprint

import builtins

import ww

from ww.utils import renamed_argument


# TODO: test that on all iterables
class BaseIterableWrapper(object):
    """ Common iterable behavior """

    def list(self):
        """ Convert self to list.

            This is provided on list as well to allow calling it all all
            ww's iterables without worring.
        """
        return ww.l(self)

    def tuple(self):
        """ Convert self to tuple.

            This is provided on tuple as well to allow calling it all all
            ww's iterables without worring.
        """
        return tuple(self)

    def str(self):
        """ Convert self to str.

            This is provided on str as well to allow calling it all all
            ww's iterables without worring.
        """
        return ww.s(self)

    def set(self):
        """ Convert self to set.

            This is provided on set as well to allow calling it all all
            ww's iterables without worring.
        """
        return builtins.set(self)

    def g(self):
        """ Convert self to g.

            This is provided on g as well to allow calling it all all
            ww's iterables without worring.
        """
        return ww.g(self)

    # TODO: offer optionnaly a better pprint
    # TODO: define all arguments explicitly
    # TODO: g() should have some information about self.iterable
    def pp(self, *args, **kwargs):
        return pprint(self, *args, **kwargs)

    @renamed_argument('key', 'keyfunc')
    def sorted(self, keyfunc=None, reverse=False):
        """ Return a new sorted iterable

            Args:
                keyfunc: A callable that must accept the current element to
                         sort and return the object used to determine it's
                         position. Default to return the object itselt.
                reverse: If True, the iterable is sorted in the descending
                         order instead of ascending. Default is False.

            Returns:
                The sorted iterable.

            Example:

                >>> from ww import l
                >>> animals = ['dog', 'cat', 'zebra', 'monkey']
                >>> for animal in l(animals).sorted():
                ...     print(animal)
                cat
                dog
                monkey
                zebra
                >>> for animal in l(animals).sorted(reverse=True):
                ...     print(animal)
                zebra
                monkey
                dog
                cat
                >>> for animal in l(animals).sorted(lambda animal: animal[-1]):
                ...     print(animal)
                zebra
                dog
                cat
                monkey
        """
        # using builtins to avoid shadowing
        lst = builtins.sorted(self, key=keyfunc, reverse=reverse)
        return self.__class__(lst)


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


    # TODO: add a sort_func argument to allow to choose the sorting strategy
    # and remove the reverse argument
    def groupby(self,
                keyfunc=None,  # type: Callable[T]
                reverse=False,  # type: bool
                cast=tuple  # type: Callable[T2]
                ):  # type: (...) -> IterableWrapper[tuple[T, T2]]
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
        gen = ww.tools.iterables.groupby(self, keyfunc, reverse, cast)  
        # TODO: remove that so that we get a g()
        return self.__class__(gen)

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
        uniques = ww.tools.iterables.skip_duplicates(self.iterator, key, fingerprints)
        # TODO: return g()
        return self.__class__(uniques)
