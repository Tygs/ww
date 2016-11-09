# coding: utf-8

from pprint import pprint

import builtins

import ww


class BaseWrapper(object):

    def list(self):
        return ww.l(self)

    def tuple(self):
        return tuple(self)

    def str(self):
        return ww.s(self)

    def set(self):
        return builtins.set(self)

    # TODO: offer optionnaly a better pprint
    # TODO: define all arguments explicitly
    def pprint(self, *args, **kwargs):
        return pprint(self, *args, **kwargs)
