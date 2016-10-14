# coding: utf-8

"""
    StringWrapper is a convenient wrapper around strings. It behaves
    like strings (the API is compatible), but make small improvements to the
    existing methods and add some new methods.

    Example:

        Import::

            >>> from ww import s

        You always have the more explicit import at your disposal::

            >>> from ww.string_wrapper import StringWrapper

        `s` is just an alias of StringWrapper, but it's what most people will
        want to use most of the time. Hence it's what we will use in the
        examples.

        Basic usages::

            >>> string = s("this is a test")
            >>> string
            u'this is a test'
            >>> type(string)
            <class 'ww.string_wrapper.StringWrapper'>
            >>> string.upper() # regular string methods are all there
            u'THIS IS A TEST'
            >>> string[:4] + "foo" # same behaviors you expect from a string
            u'thisfoo'

        Some existing methods, while still compatible with the previous
        behavior, have been improved::

            >>> string.replace('e', 'a') # just as before
            u'this is a tast'
            >>> string.replace(('e', 'i'), ('a', 'o')) # and a little more
            u'thos os a tast'
            >>> s('-').join(range(10))  # join() autocast to string
            u'0-1-2-3-4-5-6-7-8-9'
            >>> s('-').join(range(10), template="{:.2f}")
            u'0.00-1.00-2.00-3.00-4.00-5.00-6.00-7.00-8.00-9.00'

        Some methods have been added::

            >>> print(s('''
            ... This should be over indented.
            ... But it will not be.
            ... Because dedent() calls textwrap.dedent() on the string.
            ... ''').dedent())
            <BLANKLINE>
            This should be over indented.
            But it will not be.
            Because dedent() calls textwrap.dedent() on the string.
            <BLANKLINE>

        By overriding operators, we can provide some interesting syntaxic
        sugar, such as this shortcut for writting long dedented text::

            >>> print(s >> '''
            ... Calling dedent() is overrated.
            ... Overriding __rshift__ is much more fun.
            ... ''')
            <BLANKLINE>
            Calling dedent() is overrated.
            Overriding __rshift__ is much more fun.
            <BLANKLINE>

        Also we hacked something that looks like Python 3.6 f-string, but
        that works in Python 2.7 and 3.3+:

            >>> a = 1
            >>> f('Sweet, I can print locals: {a}')
            u'Sweet, I can print locals: 1'
            >>> print(f >> '''
            ... Yes it works with long string too.
            ... And globals, if you are into that kind
            ... of things.
            ... But we have only {a} for now.
            ... ''')
            <BLANKLINE>
            Yes it works with long string too.
            And globals, if you are into that kind
            of things.
            But we have only 1 for now.
            <BLANKLINE>

        There is much, much more...

        You'll find bellow the detailed documentation for each method of
        StringWrapper. Go have a look, there is some great stuff here!
"""

from __future__ import (absolute_import, division, print_function)

# TODO: add home link button to documention web page
# TODO : flags can be passed as strings. Ex: s.search('regex', flags='ig')
# TODO : make s.search(regex) return a wrapper with __bool__ evaluating to
# false if no match instead of None and allow default value for group(x)
# also allow match[1] to return group(1) and match['foo'] to return
# groupdict['foo']
# TODO .groups would be a g() object
# TODO: .pp() to pretty_print
# TODO: override slicing to return part s

# TODO : add encoding detection, fuzzy_decode() to make the best of shitty
# decoding, unidecode, slug, etc,


# f() for format, if no args are passed, it uses local. Also allow f >> ""

# t() or t >> for a jinja2 template (optional dependency ?)
# something for translation ?

# TODO: match.__repr__ should show match, groups, groupsdict in summary

import re
import inspect

from textwrap import dedent

import six
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


try:
    unicode = unicode  # type: ignore
except NameError:
    unicode = str


FORMATTER = LiteralFormatter()


class MetaS(type):
    """ Allow s >> 'text' as a shortcut to dedent strings """

    def __rshift__(self, other):
        # TODO: figure out how to allow this to work with subclasses
        return StringWrapper(dedent(other))


class MetaF(type):
    """ Allow f >> 'text' as a shortcut to dedent f-string """

    def __rshift__(self, other):
        caller_frame = inspect.currentframe().f_back
        caller_globals = caller_frame.f_globals
        caller_locals = caller_frame.f_locals
        # TODO: figure out how to allow StringWrapper subclasses to work
        # with this
        return StringWrapper(dedent(
            FORMATTER.format(other, caller_globals, caller_locals)
        ))


# TODO: refactor methods to be only wrappers
#       for functions from a separate module
# TODO: override capitalize, title, upper, lower, etc
class StringWrapper(with_metaclass(MetaF, unicode)):  # type: ignore

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

    # kwargs allow compat with 2.7 and 3 since you can't use
    # keyword-only arguments in python 2
    # TODO: remove empty strings
    # TODO: wrap output in StringWrapper
    def split(self, *separators, **kwargs):  # type: ignore
        # type: (*str, int, str) -> list[StringWrapper]
        """ Like str.split, but accept several separators and regexes

            Args:
                separators: strings you can split on. Each string can be a
                            regex.
                maxsplit: max number of time you wish to split. default is 0,
                          which means no limit.
                flags: flags you wish to pass if you use regexes. You should
                       pass them as a string containing a combination of:

                        - 'm' for re.MULTILINE
                        - 'x' for re.VERBOSE
                        - 'v' for re.VERBOSE
                        - 's' for re.DOTALL
                        - '.' for re.DOTALL
                        - 'd' for re.DEBUG
                        - 'i' for re.IGNORECASE
                        - 'u' for re.UNICODE
                        - 'l' for re.LOCALE

            Example:

                >>> string = s('fat     black cat, big bad dog')
                >>> string.split().list()
                [u'fat', u'black', u'cat,', u'big', u'bad', u'dog']
        """
        # TODO, when separator is empty, make it split on non printable
        # caracters

        maxsplit = kwargs.get('maxsplit', 0)  # 0 means "no limit" for re.split
        if not separators:  # TODO: pass maxsplit
            maxsplit = maxsplit or -1  # -1 means "no limit" for unicode.split
            return g(map(self.__class__, unicode.split(self, None, maxsplit)))

        for sep in separators:
            if not isinstance(sep, basestring):
                msg = s >> """
                    Separators must be string, not "{sep}" ({sep_type}).
                    A common cause of this error is to call split([a, b, c])
                    instead of split(a, b, c).
                """.format(sep=sep, sep_type=type(sep))
                raise TypeError(msg)

        # TODO: split let many spaces. Fix it.

        flags = self._parse_flags(kwargs.get('flags', 0))
        return g(map(self.__class__, self._split(separators, maxsplit, flags)))

    def _split(self, separators, maxsplit=0, flags=0):
        try:
            sep = separators[0]
            # TODO: find a better error message

            # TODO: maxsplit is buggy, fix it
            separators = separators[1:]
            for chunk in re.split(sep, self, maxsplit, flags):
                chunk = self.__class__(chunk)
                for item in chunk._split(separators, maxsplit=0, flags=0):
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

        return self.__class__(res)

    def dedent(self):
        return self.__class__(dedent(self))

    def upper(self):
        return self.__class__(unicode.upper(self))

    def __getitem__(self, index):
        return self.__class__(unicode.__getitem__(self, index))

    def __add__(self, other):
        return self.__class__('{}{}').format(self, other)

    def join(self, iterable, formatter=lambda s, t: t.format(s),
             template="{}"):
        formatted_iterable = (formatter(st, template) for st in iterable)
        return self.__class__(unicode.join(self, formatted_iterable))

    @classmethod
    def from_bytes(cls, byte_string, encoding=None, errors='strict'):
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

        return cls(byte_string.decode(encoding, errors=errors))

    def format(self, *args, **kwargs):
        if not args and not kwargs:
            pframe = inspect.currentframe().f_back
            return self.__class__(unicode.format(self, **pframe.f_locals))
        return self.__class__(unicode.format(self, *args, **kwargs))

    def to_bool(self, default=None):
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
            }[self.casefold()]
        except KeyError:
            if default is not None:
                return default
            raise ValueError(f >> """
                             '{vals!r}' cannot be converted to a boolean. Clean
                             your input or set the 'default' parameter to True
                             or False.
                             """)
    if six.PY3:  # we want unified representation between versions
        def __repr__(self):
            return 'u{}'.format(super(StringWrapper, self).__repr__())

# shortcut from StringWrapper
s = StringWrapper


# TODO: make sure each class call self._class instead of s(), g(), etc
class f(with_metaclass(MetaF)):  # type: ignore

    def __new__(cls, string):
        caller_frame = inspect.currentframe().f_back
        caller_globals = caller_frame.f_globals
        caller_locals = caller_frame.f_locals
        return StringWrapper(FORMATTER.format(string, caller_globals,
                                              caller_locals))
