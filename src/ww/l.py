


class l(list):

    def len(self):
        return len(self)

    def join(self, iterable, formatter=lambda s, t: t.format(s), template="{}"):
        return  s.join(iterable, formatter, template)

    def append(self, *values):
        for value in values:
            self.append(value)


    # todo : remplement slicing like g()