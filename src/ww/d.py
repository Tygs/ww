# TODO: d.fromkeys(keys, callable|value)
# TODO: d.merge
# TODO: d.swap (swap keys and values)
# TODO: iterating on it alway return (key, val)
# TODO: add()


class d(dict):

    def isubset(self, *keys):
        for key in keys:
            yield key, self[key]

    def subset(self, *keys):
        return d(self.isubset(*keys))
