# coding: utf-8

from __future__ import (absolute_import,
                        division, print_function)


# TODO : make a s object for strings with split(regex|iterable),
# replace(regex|iterable)
# TODO : flags can be passed as strings. Ex: s.search('regex', flags='ig')
# TODO : make s.search(regex) return a wrapper with __bool__ evaluating to
# false if no match instead of None and allow default value for group(x)
# also allow match[1] to return group(1) and match['foo'] to return
# groupdict['foo']
# TODO .groups would be a g() object


# TODO : add encoding detection, fuzzy_decode() to make the best of shitty
# decoding, unidecode, slug, etc,


# f() for format, if no args are passed, it uses local. Also allow f >> ""

# t() or t >> for a jinja2 template (optional dependency ?)
# something for translation ?


# TODO: match.__repr__ should show match, groups, groupsdict in summary

import re
import inspect

from textwrap import dedent

import chardet

try:
    from formatizer import LiteralFormatter
    FORMATTER = LiteralFormatter()
except ImportError:
    FORMATTER = str

from six import with_metaclass
from past.builtins import basestring

from .g import g
from .utils import ensure_tuple

# TODO: make sure we copy all methods from str but return s()

try:
    unicode = unicode
except NameError:
    unicode = str


REGEX_FLAGS = {
    'm': re.MULTILINE,
    'x': re.VERBOSE,
    'v': re.VERBOSE,
    's': re.DOTALL,
    '.': re.DOTALL,
    'd': re.DEBUG,
    'i': re.IGNORECASE,
    'u': re.UNICODE,
    'l': re.LOCALE,
}

try:
    # Python2 doesn't support re.ASCII flag
    REGEX_FLAGS['a'] = re.ASCII
except AttributeError:
    pass

FORMATTER = LiteralFormatter()


class MetaS(type):
    """ Allow s >> 'text' as a shortcut to dedent strings """

    def __rshift__(self, other):
        return s(dedent(other))


class MetaF(type):
    """ Allow f >> 'text' as a shortcut to dedent f-string """

    def __rshift__(self, other):
        caller_frame = inspect.currentframe().f_back
        caller_globals = caller_frame.f_globals
        caller_locals = caller_frame.f_locals
        return s(dedent(
                 FORMATTER.format(other, caller_globals, caller_locals)
                 ))


class StringWrapper(with_metaclass(MetaS, unicode)):

    # TODO: check for bytes in __new__. Say we don't accept it and recommand
    # to either use u'' in front of the string, from __future__ or
    # s.from_bytes(bytes, encoding)

    def _parse_flags(self, flags):
        bflags = 0
        if isinstance(flags, basestring):
            for flag in flags:
                bflags |= REGEX_FLAGS[flag]

            return bflags

        return flags

    def split(self, *separators, **kwargs):

        for sep in separators:
            if not isinstance(sep, basestring):
                msg = s >> """
                    Separators must be string, not "{sep}" ({sep_type}).
                    A common cause of this error is to call split([a, b, c])
                    instead of split(a, b, c).
                """.format(sep=sep, sep_type=type(sep))
                raise TypeError(msg)

        return g(self._split(separators, kwargs.get('maxsplit', 0),
                             self._parse_flags(kwargs.get('flags', 0))))

    def _split(self, separators, maxsplit=0, flags=0):
        try:
            sep = separators[0]
            # TODO: find a better error message

            for chunk in re.split(sep, self, maxsplit, flags):
                for item in s(chunk)._split(separators[1:],
                                            maxsplit=0, flags=0):
                    yield item
        except IndexError:
            yield self

    def replace(self, patterns, substitutions, maxreplace=0, flags=0):

        patterns = ensure_tuple(patterns)
        substitutions = ensure_tuple(substitutions)

        num_of_subs = len(substitutions)
        num_of_patterns = len(patterns)
        if num_of_subs == 1:
            substitutions *= num_of_patterns
        else:
            if len(patterns) != num_of_subs:
                raise ValueError("You must have exactly one substitution "
                                 "for each pattern or only one substitution")

        flags = self._parse_flags(flags)

        res = self
        for pattern, sub in zip(patterns, substitutions):
            res = re.sub(pattern, sub, res, count=maxreplace, flags=flags)

        return s(res)

    def dedent(self):
        return s(dedent(self))

    def join(self, iterable, formatter=lambda s, t: t.format(s),
             template="{}"):
        return s(unicode.join(self,
                              (formatter(st, template) for st in iterable)))

    @staticmethod
    def from_bytes(byte_string, encoding=None, errors='strict'):
        if encoding is None:
            encoding = chardet.detect(byte_string)['encoding']
            raise ValueError(f >> """
                             from_bytes() expects a second argument:
                             'encoding'. If you don't know which encoding,
                             try '{encoding}' or 'utf8'. If it fails and you
                             can't find out what has been used, you can get
                             a partial decoding with encoding="ascii" and
                             errors='replace' or 'ignore'.
                             """)

        return s(byte_string.decode(encoding, errors=errors))

    def format(self, *args, **kwargs):
        if not args and not kwargs:
            pframe = inspect.currentframe().f_back
            return s(unicode.format(self, **pframe.f_locals))
        return s(unicode.format(self, *args, **kwargs))

    def to_bool(self, val, default=None):
        try:
            return {
                '1': True,
                '0': False,
                'true': True,
                'false': False,
                'on': True,
                'off': False,
                'yes': True,
                'no': False,
                '': False
            }[val.casefold()]
        except KeyError:
            if default is not None:
                return default
            raise ValueError(f >> """
                             '{vals!r}' cannot be converted to a boolean. Clean
                             your input or set the 'default' parameter to True
                             or False.
                             """)

# shortcut from StringWrapper
s = StringWrapper


# TODO: make sure each class call self._class instead of s(), g(), etc
class f(with_metaclass(MetaF)):

    def __new__(cls, string):
        caller_frame = inspect.currentframe().f_back
        caller_globals = caller_frame.f_globals
        caller_locals = caller_frame.f_locals
        return s(FORMATTER.format(string, caller_globals, caller_locals))
