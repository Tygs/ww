# coding: utf-8

import ww


# TODO: allow subclass to chose the string class
class ListWrapper(list):

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
