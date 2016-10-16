# coding: utf-8

from pprint import pprint

import builtins

import ww


class BaseWrapper(object):

    def list(self):
        return builtins.list(self)

    def wlist(self):
        return ww.l(self)

    def tuple(self):
        return builtins.tuple(self)

    def wtuple(self):
        return ww.t(self)

    def str(self):
        return builtins.str(self)

    def wstr(self):
        return ww.s(self)

    def set(self):
        return builtins.set(self)

    def wset(self):
        return NotImplemented

    # TODO: offer optionnaly a better pprint
    # TODO: define all arguments explicitly
    def pprint(self, *args, **kwargs):
        return pprint(self, *args, **kwargs)
