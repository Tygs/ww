# coding: utf-8

import builtins

import ww

# TODO: ease creation of multi dimensional array
# TODO: allow subclass to chose the string class
# TODO: list.build(*dimensions, default=value) as a wrapper for data.matrix
# TODO: similar things for sets, bytes,
# TODO: test automethods
# TODO: delegate work on utils


from ww.utils import ensure_callable, auto_methods

# List of methods returning None that we want to automatically
# return self. We plug them in a loop at the end
# of this file
AUTO_METHODS = ('sort', 'insert', 'clear', 'remove')


class ListWrapper(ww.wrappers.base.BaseIterableWrapper):

    @property
    def len(self):
        """Return object length

        Example:

            >>> from ww import l
            >>> lst = l([0, 1, 2, 3])
            >>> lst.len
            4
        """

        return len(self)

    def join(self, joiner, formatter=lambda s, t: t.format(s),
             template="{}"):
        """Join values and convert to string

        Example:

            >>> from ww import l
            >>> lst = l('012')
            >>> lst.join(',')
            u'0,1,2'
            >>> lst.join(',', template="{}#")
            u'0#,1#,2#'
            >>> string = lst.join(',',\
                                  formatter = lambda x, y: str(int(x) ** 2))
            >>> string
            u'0,1,4'
        """

        return ww.s(joiner).join(self, formatter, template)

    def append(self, *values):
        """Append values at the end of the list

        Allow chaining.

        Args:
            values: values to be appened at the end.

        Example:

            >>> from ww import l
            >>> lst = l([])
            >>> lst.append(1)
            [1]
            >>> lst
            [1]
            >>> lst.append(2, 3).append(4,5)
            [1, 2, 3, 4, 5]
            >>> lst
            [1, 2, 3, 4, 5]
        """

        for value in values:
            list.append(self, value)
        return self

    def extend(self, *iterables):
        """Add all values of all iterables at the end of the list

        Args:
            iterables: iterable which content to add at the end

        Example:

            >>> from ww import l
            >>> lst = l([])
            >>> lst.extend([1, 2])
            [1, 2]
            >>> lst
            [1, 2]
            >>> lst.extend([3, 4]).extend([5, 6])
            [1, 2, 3, 4, 5, 6]
            >>> lst
            [1, 2, 3, 4, 5, 6]
        """

        for value in iterables:
            list.extend(self, value)
        return self

    # TODO: proper arguments
    def sort(self, *args, **kwargs):
        super(list, self).sort(*args, **kwargs)
        return self

    def clear(self):
        super(list, self).clear()
        return self

    def copy(self):
        return self.__class__(self)

    def insert(self, index, object):
        super(list, self).clear(index, object)
        return self

    def pop_or(self, index, default=None):
        try:
            return self.pop(index)
        except IndexError:
            return ensure_callable(default)()

    def remove(self, index):
        super(list, self).remove(index, object)
        return self

    def map(self, callable):
        # type: (Callable) -> ListWrapper
        """ Shortcut method to l(map(self))

            Args:
                call: the callable to pass to map()

            Example:

                >>> from ww import l
                >>> l(range(3)).map(str)
                ['0', '1', '2']

        """
        return self.__class__(builtins.map(callable, self))


    def filter(self, callable):
        # type: (Callable) -> ListWrapper
        """ Shortcut method to l(filter(self))

            Args:
                call: the callable to pass to filter()

            Example:

                >>> from ww import l
                >>> l(range(3)).filter(bool)
                [1, 2]

        """
        return self.__class__(builtins.filter(callable, self))

    def zip(self, *others):
        # type: (*Iterable) -> ListWrapper
        """ Shortcut method to l(zip(self))

            Args:
                others: the iterables to pass to zip()

            Example:

                >>> from ww import l
                >>> for element in l(range(3)).zip("abc"):
                ...     print(*element)
                0 a
                1 b
                2 c
                >>> for element in l(range(3)).zip("abc", [True, False, None]):
                ...    print(*element)
                0 a True
                1 b False
                2 c None
        """
        return self.__class__(builtins.zip(self, *others))


auto_methods(ListWrapper, list, AUTO_METHODS, force_chaining=True)

