


class l(list):

    @property
    def len(self):
        """Return len(self)
            
        Example:

            >>> list = [0, 1, 2, 3]
            >>> list.len
            4
        """
        
        return len(self)

    def join(self, iterable, formatter=lambda s, t: t.format(s), template="{}"):
    
        return  s.join(iterable, formatter, template)

    def append(self, *values):
        """Append values at the end of the list
        
        Allow chaining.

        Args:
            values: values to be appened at the end.

        Example:

            >>> lst = l([])
            >>> lst.append(1)
            >>> lst
            [1]
            >>> lst.append(2, 3).append(4,5)
            >>> lst
            [1, 2, 3, 4, 5]
        """
        
        for value in values:
            list.append(self, value)
        return self
    # todo : remplement slicing like g()
    
    def extend(self, *values):
        """Chaining Extend *values on self

        Args:
            *values: iterable to use for the iner state.

        Example:

            >>> lst = l([])
            >>> lst.extend([1, 2])
            >>> lst
            [1, 2]
            >>> lst.extend([3, 4]).extend([5, 6])
            >>> lst
            [1, 2, 3, 4, 5, 6]
        """
        
        for value in values:
            list.extend(self, value)
        return self
    
