
from pprint import pprint

import ww


class BaseWrapper(object):

    def list(self):
        return __builtins__.list(self)

    def wlist(self):
        return ww.l(self)

    def tuple(self):
        return __builtins__.tuple(self)

    def wtuple(self):
        return ww.t(self)

    def str(self):
        return __builtins__.str(self)

    def wstr(self):
        return ww.s(self)

    # TODO: offer optionnaly a better pprint
    # TODO: define all arguments explicitly
    def pprint(self, *args, **kwargs):
        return pprint(self, *args, **kwargs)
