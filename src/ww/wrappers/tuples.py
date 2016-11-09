# TODO: anonymous namedtuple that can be created inline
# TODO: tuples can be either with names or not (but not both)

import ww


# TODO: inherit from BaseWrapper
class TupleWrapper(tuple):
    @property
    def len(self):
        return len(self)

    def join(self, joiner, formatter=lambda s, t: t.format(s),
             template="{}"):
        """Join values and convert to string

        Example:

            >>> from ww import t
            >>> lst = t('012')
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

    def index(self, value):
        """
        Args:
            value: index

        Returns: index of the values

        Raises:
            ValueError: value is not in list
        """

        for i, x in enumerate(self):
            if x == value:
                return i

        raise ValueError("{} is not in list".format(value))

    def to_l(self):
        """
        Args: self

        Returns: a l that stems from self
        """
        return ww.l(self)

    # TODO: rename this method to dict()
    def to_d(self):
        """
        Args: self

        Returns: a d that stems from self

        Raises:
            ValueError: dictionary update sequence element #index has length
            len(tuple); 2 is required

            TypeError: cannot convert dictionary update sequence element
            #index to a sequence
        """

        try:
            return ww.d(self)
        except (TypeError, ValueError):

            for i, element in enumerate(self):
                try:
                    iter(element)

                # TODO: find out why we can't cover this branch. The code
                # is tested but don't appear in coverage
                except TypeError:  # pragma: no cover
                    # TODO: use raise_from ?
                    raise ValueError(("'{}' (position {}) is not iterable. You"
                                      " can only create a dictionary from a "
                                      "elements that are iterables, such as "
                                      "tuples, lists, etc.")
                                     .format(element, i))

                try:
                    size = len(element)
                except TypeError:  # ignore generators, it's already consummed
                    pass
                else:
                    raise ValueError(("'{}' (position {}) contains {} "
                                      "elements. You can only create a "
                                      "dictionary from iterables containing "
                                      "2 elements.").format(element, i, size))

            raise
