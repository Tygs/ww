# coding: utf-8

"""
    ww contains convenient wrappers around strings. The Most important one is
    StringWrapper, that you will mostly use as the "s()" object.

    It behaves like unicode strings (the API is compatible),
    but make small improvements to the existing methods and add some new
    methods.

    It doesn't accept bytes as an input. If you do so and it works, you must
    know it's not a supported behavior and may change in the future. Only
    pass:

    - unicode objects in Python 2;
    - str objects in Python 3.

    Example:

        Import::

            >>> from ww import s

        You always have the more explicit import at your disposal::

            >>> from ww.wrappers.strings import StringWrapper

        `s` is just an alias of StringWrapper, but it's what most people will
        want to use most of the time. Hence it's what we will use in the
        examples.

        Basic usages::

            >>> string = s("this is a test")
            >>> string
            u'this is a test'
            >>> type(string)
            <class 'ww.wrappers.strings.StringWrapper'>
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

            >>> from ww import f
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

        .. warning::

           Remember that, while f-strings are interpreted at parsing time,
           our implementation is executed at run-time, making it vulnerable
           to code injection. This makes it a dangerous feature to put in
           production.

        There is much, much more to play with. Check it out :)

    You'll find bellow the detailed documentation for each method of
    StringWrapper. Go have a look, there is some great stuff here!
"""

from __future__ import (absolute_import, division, print_function)

# TODO : flags can be passed as strings. Ex: s.search('regex', flags='ig')
# TODO : make s.search(regex) return a wrapper with __bool__ evaluating to
# false if no match instead of None and allow default value for group(x)
# also allow match[1] to return group(1) and match['foo'] to return
# groupdict['foo']
# TODO .groups would be a g() object
# TODO: .pp() to pretty_print
# TODO: override slicing to allow callables
# TODO: provide "strip_comments" ?
# TODO: provide from_json() / to_json()
# TODO: provide the same for html / xml

# TODO : add encoding detection, fuzzy_decode() to make the best of shitty
# decoding, unidecode, slug, etc,

# tpl() or tpl >> for a jinja2 template (optional dependency ?)
# something for translation ?

# TODO: match.__repr__ should show match, groups, groupsdict in summary

import inspect

from textwrap import dedent

import six
import chardet

from future.utils import raise_from

try:
    from formatizer import LiteralFormatter
    FORMATTER = LiteralFormatter()
except ImportError:  # pragma: no cover
    FORMATTER = str

from six import with_metaclass

import ww
from ww.tools.strings import multisplit, multireplace
from ww.types import (Union, unicode, str_istr, str_istr_icallable,  # noqa
                      C, I, Iterable, Callable, Any)

# TODO: make sure we copy all methods from str but return s()

FORMATTER = LiteralFormatter()


# TODO: s >> should do s().strip().dedent().fold()
class MetaS(type):
    """ Allow s >> 'text' as a shortcut to dedent strings

        This is not something you should use directly. It's a metaclass
        for s() StringWrapper objects and is used to override the
        operator >> on the StringWrapper class (not the object).
    """

    def __rshift__(self, other):
        # type (str) -> StringWrapper
        """ Let you do s >> "a string" as a shortcut to s("a string").dedent()

            s is the class, not s(), which would be an instance.

            Args:
                other: the string at the right of the '>>' operator.

            Returns:
                The dedented string as wrapped in StringWrapper. Right now
                we always return StringWrapper, so subclassing won't work
                if you want to override this.

            Raises:
                TypeError: if you try to apply it on non strings.

            Example:

                >>> from ww import s
                >>> print(s >> '''
                ...     This should be indented
                ...     but it will not be
                ... ''')
                <BLANKLINE>
                This should be indented
                but it will not be
                <BLANKLINE>
        """
        # TODO: figure out how to allow this to work with subclasses
        return StringWrapper(dedent(other))


class MetaF(type):
    """ Allow f >> 'text' as a shortcut to dedent f-like-strings.

        This is not something you should use directly. It's a metaclass
        for s() StringWrapper objects and is used to override the
        operator >> on the StringWrapper class (not the object).

        This is the same as MetaS, but it wraps the string in f(), not in
        s(), meaning you can use the f-string compatible syntax inside
        the string you wish to dedent.

        .. warning::

           Remember that, while f-strings are interpreted at parsing time,
           our implementation is executed at run-time, making it vulnerable
           to code injection. This makes it a dangerous feature to put in
           production.
    """

    def __rshift__(self, other):
        # type (str) -> StringWrapper
        """ Let you do f >> "a string" as a shortcut to f("a string").dedent()

            f is the class, not f(), which would be an instance.

            Args:
                other: the string at the right of the '>>' operator.

            Returns:
                The dedented string as wrapped in StringWrapper. Right now
                we always return StringWrapper, so subclassing won't work
                if you want to override this.

            Raises:
                TypeError: if you try to apply it on non strings.

            Example:

                >>> from ww import f
                >>> var = "foo"
                >>> print(f >> '''
                ...     This should be indented
                ...     but it will not be.
                ...     And you can use {var}.
                ... ''')
                <BLANKLINE>
                This should be indented
                but it will not be.
                And you can use foo.
                <BLANKLINE>

            .. warning::

               Remember that, while f-strings are interpreted at parsing
               time, our implementation is executed at run-time, making it
               vulnerable to code injection. This makes it a dangerous feature
               to put in production.
        """
        caller_frame = inspect.currentframe().f_back
        caller_globals = caller_frame.f_globals
        caller_locals = caller_frame.f_locals
        # TODO: figure out how to allow StringWrapper subclasses to work
        # with this
        return StringWrapper(dedent(
            FORMATTER.format(other, caller_globals, caller_locals)
        ))


# TODO: add normalize() (removes special caracters) and slugify
# (normalize + slug)
# TODO: refactor methods to be only wrappers
#       for functions from a separate module
# TODO: override capitalize, title, upper, lower, etc
# TODO: inherit from BaseWrapper
class StringWrapper(with_metaclass(MetaS, unicode)):  # type: ignore
    """
        Convenience wrappers around strings behaving like unicode strings, but
        make small improvements to the existing methods and add some new
        methods.

        It doesn't accept bytes as an input. If you do so and it works, you
        must know it's not a supported behavior and may change in the future.
        Only pass:

        - unicode objects in Python 2;
        - str objects in Python 3.

        Basic usages::

            >>> from ww import s
            >>> string = s("this is a test")
            >>> string
            u'this is a test'
            >>> type(string)
            <class 'ww.wrappers.strings.StringWrapper'>
            >>> string.upper() # regular string methods are all there
            u'THIS IS A TEST'
            >>> string[:4] + "foo" # same behaviors you expect from a string
            u'thisfoo'
            >>> string.split(u'a', u'i', u'e')  # lots of features are improved
            <IterableWrapper generator>
            >>> string.split(u'a', u'i', u'e').list()
            [u'th', u's ', u's a t', u'st']
    """
    # TODO: allow subclasses to choose iterable wrapper classes

    # TODO: check for bytes in __new__. Say we don't accept it and recommand
    # to either use u'' in front of the string, from __future__ or
    # s.from_bytes(bytes, encoding)

    # kwargs allows compatibilit with 2.7 and 3 since you can't use
    # keyword-only arguments in python 2
    def split(self,
              *separators,  # type: StringWrapper
              **kwargs  # Union[str, C[..., I[StringWrapper]]]
              ):  # type (...) -> I[StringWrapper]
        """ Like unicode.split, but accept several separators and regexes

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

            Returns:
                An iterable of substrings.

            Raises:
                ValueError: if you pass a flag without separators.
                TypeError: if you pass something else than unicode strings.

            Example:

                >>> from ww import s
                >>> string = s(u'fat     black cat, big bad dog')
                >>> string.split().list()
                [u'fat', u'black', u'cat,', u'big', u'bad', u'dog']
                >>> string = s(u'a,b;c/d=a,b;c/d')
                >>> string.split(u',', u';', u'[/=]', maxsplit=4).list()
                [u'a', u'b', u'c', u'd', u'a,b;c/d']
        """
        kwargs.setdefault('cast', ww.l)
        chunks = multisplit(self, *separators, **kwargs)  # type: Iterable[str]
        return ww.g(chunks).map(self.__class__)

    def replace(self,
                patterns,  # type: str_istr
                substitutions,  # type: str_istr_icallable
                maxreplace=0,  # type: int
                flags=0  # type: unicode
                ):  # type: (...) -> StringWrapper
        """ Like unicode.replace() but accept several substitutions and regexes

            Args:
                patterns: a string, or an iterable of strings to be replaced.
                substitutions: a string or an iterable of string to use as a
                               replacement. You can pass either one string, or
                               an iterable containing the same number of
                               sustitutions that you passed as patterns. You
                               can also pass a callable instead of a string. It
                               should expact a match object as a parameter.
                maxreplace: the max number of replacement to make. 0 is no
                            limit, which is the default.
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

            Returns:
                The string with replaced bits, wrapped with StringWrapper.

            Raises:
                ValueError: if you pass the wrong number of substitution.

            Example:

                >>> from __future__ import unicode_literals
                >>> from ww import s
                >>> s('a,b;c/d').replace((',', ';', '/'), ',')
                u'a,b,c,d'
                >>> s('a1b33c-d').replace('\d+', ',')
                u'a,b,c-d'
                >>> s('a-1,b-3,3c-d').replace('[,-]', '', maxreplace=3)
                u'a1b3,3c-d'
                >>> def upper(match):
                ...     return match.group().upper()
                ...
                >>> s('a-1,b-3,3c-d').replace('[ab]', upper)
                u'A-1,B-3,3c-d'
        """
        res = multireplace(self, patterns, substitutions, maxreplace, flags)
        return self.__class__(res)

    # TODO: add a "strip_white_ends" and "remove_lone_linebreaks" param
    def dedent(self):
        # type: (...) -> StringWrapper
        """ Call texwrap.dedent() on the string, removing useless indentation

            Returns:
                The strings without indentation and wrapped with StringWrapper.

            Example:

                >>> from ww import s
                >>> print(s('''
                ...     This should be indented
                ...     but it will not be
                ... ''').dedent())
                <BLANKLINE>
                This should be indented
                but it will not be
                <BLANKLINE>
        """
        return self.__class__(dedent(self))

    def upper(self):
        # type: (...) -> StringWrapper
        """ Call str.upper() on the string, making it uppercase.

            Returns:
                The upper cased string, wrapped in StringWrapper.

            Example:

                >>> from ww import s
                >>> print(s('Foo').upper())
                FOO
                >>> type(s('Foo').upper())
                <class 'ww.wrappers.strings.StringWrapper'>
        """
        return self.__class__(unicode.upper(self))

    # TODO: add the same features as getitems on g()
    def __getitem__(self, index):
        # type: (Union[int, slice]) -> StringWrapper
        """ Make indexing/slicing return s() objects.

            Returns:
                The result of the indexing/slicing, wrapped in StringWrapper

            Raises:
                IndexError: if the index if greater than the string length.
                TypeError: if the index is not an integer.

            Example:

                >>> from ww import s
                >>> s('Foo')[0]
                u'F'
                >>> type(s('Foo')[0])
                <class 'ww.wrappers.strings.StringWrapper'>
        """

        return self.__class__(unicode.__getitem__(self, index))

    # TODO: override '//' so that it does like '+' but autocast.
    def __add__(self, other):
        # type: (str) -> StringWrapper
        """ Concatenate the 2 strings, but wraps it in s().

            Args:
                other: The other string to concatenate with the current one.

            Raises:
                TypeError: raised one of the concatenated objects is not
                           a string.

            Returns:
                The concatenated string wrapped in StringWrapper.

            Example:

                >>> from ww import s
                >>> s(u'a') + u'b'
                u'ab'
                >>> type(s(u'a') + u'b')
                <class 'ww.wrappers.strings.StringWrapper'>
        """

        # forbid concatenation with bytes, even in Python 2.
        if isinstance(other, bytes):
            raise TypeError(ww.s >> """
                The string "{!r}" and the bytes "{!r}" cannot be
                concatenated. You need to decode the bytes to convert them to
                a string first. One way to do it is to call the decode()
                method.

                Example:

                    text_as_string = text_as_bytes.decode(text_encoding)

                If you don't know what encoding to use, try 'utf8', and if
                it doesn't work, google the `chardet` Python module as it can
                help you to detect it.

                Remember that in Python 2.7, bytes are confusingly
                called 'str', and strings are called 'unicode'.
            """.format(self, other))

        str_self = unicode(self)  # for p2.7 compat

        try:
            str_res = unicode.__add__(str_self, other)
        except TypeError as e:
            raise_from(e.__class__(ww.s >> """
                You can't concatenate a string ({!r}) with an object of
                type {} ({!r}).
                Python won't guess how to convert it for you, you need to
                manually do it. The most common way to do so is to call s()
                on it.
            """.format(self, type(other), other)), e)

        return self.__class__(str_res)

    def __radd__(self, other):
        # type: (str) -> StringWrapper
        """ Concatenate the 2 strings, s() being on the right of the equation.

            Args:
                other: The other string to concatenate with the current one.

            Raises:
                TypeError: raised one of the concatenated objects is not
                           a string.

            Returns:
                The concatenated string wrapped in StringWrapper.

            Example:

                >>> from ww import s
                >>> u'b' + s(u'a')
                u'ba'
                >>> type(u'b' + s(u'a'))
                <class 'ww.wrappers.strings.StringWrapper'>
        """

        # forbid concatenation with bytes, even in Python 2.
        if isinstance(other, bytes):
            raise TypeError(ww.s >> """
                The string "{!r}" and the bytes "{!r}" cannot be
                concatenated. You need to decode the bytes to convert them to
                a string first. One way to do it is to call the decode()
                method.

                Example:

                    text_as_string = text_as_bytes.decode(text_encoding)

                If you don't know what encoding to use, try 'utf8', and if
                it doesn't work, google the `chardet` Python module as it can
                help you to detect it.

                Remember that in Python 2.7, bytes are confusingly
                called 'str', and strings are called 'unicode'.
            """.format(self, other))

        str_self = unicode(self)  # for p2.7 compat

        try:
            str_res = unicode.__add__(other, str_self)
        except TypeError as e:
            raise_from(e.__class__(ww.s >> """
                You can't concatenate a string ({!r}) with an object of
                type {} ({!r}).
                Python won't guess how to convert it for you, you need to
                manually do it. The most common way to do so is to call s()
                on it.
            """.format(self, type(other), other)), e)

        return self.__class__(str_res)

    def join(self, iterable, formatter=lambda s, t: t.format(s),
             template="{}"):
        # type: (Iterable, Callable, str) -> ww.s.StringWrapper
        """ Join every item of the iterable into a string.

            This is just like the `join()` method on `str()` but with
            auto cast to a string. If you dislike auto cast, `formatter` and
            `template` let you control how to format each element.

            Args:
                iterable: the iterable with elements you wish to join.

                formatter: a the callable returning a representation of the
                           current element as a string. It will be called on
                           each element, with the element being past as the
                           first parameter and the value of `template` as the
                           second parameter.
                           The default value is to return::

                               template.format(element)

                template: a string template using the .format() syntax to be
                          used by the formatter callable.
                          The default value is "{}", so that the formatter can
                          just return::

                                "{}".format(element)


            Returns:
                The joined elements as StringWrapper

            Example:

                >>> from ww import s
                >>> s('|').join(range(3))
                u'0|1|2'
                >>> to_string = lambda s, t: str(s) * s
                >>> print(s(',').join(range(1, 4), formatter=to_string))
                1,22,333
                >>> print(s('\\n').join(range(3), template='- {}'))
                - 0
                - 1
                - 2

        """
        formatted_iterable = (formatter(st, template) for st in iterable)
        return self.__class__(unicode.join(self, formatted_iterable))

    @classmethod
    def from_bytes(cls, byte_string, encoding=None, errors='strict'):
        # type: (bytes, str, str) -> ww.s.StringWrapper
        u""" Convenience proxy to byte.decode().

            This let you decode bytes from the StringWrapper class the
            same way you would decode it from the bytes class, and
            wraps the result in StringWrapper.

            Args:
                byte_string: encoded text you wish to decode.

                encoding: the name of the character set you want to use
                          to attempt decoding.

                errors: the policy to use when encountering error while trying
                        to decode the text. 'strict', the default, will raise
                        an exception.  'ignore' will skip the faulty bits.
                        'replace' will replace them with '?'.

            Returns:
                The decoded strings wrapped in StringWrapper.

            Example:

                >>> from ww import s
                >>> utf8_text = u'Père Noël'.encode('utf8')
                >>> print(s.from_bytes(utf8_text, 'utf8'))
                Père Noël
                >>> type(s.from_bytes(utf8_text, 'utf8'))
                <class 'ww.wrappers.strings.StringWrapper'>
                >>> print(s.from_bytes(utf8_text, 'ascii', 'replace'))
                P��re No��l
                >>> print(s.from_bytes(utf8_text, 'ascii', 'ignore'))
                Pre Nol
        """
        if encoding is None:
            encoding = chardet.detect(byte_string)['encoding']
            # TODO: strip() and ignore first line ?
            raise ValueError(ww.f >> """
                             from_bytes() expects a second argument:
                             'encoding'. If you don't know which encoding,
                             try '{encoding}' or 'utf8'. If it fails and you
                             can't find out what has been used, you can get
                             a partial decoding with encoding="ascii" and
                             errors='replace' or 'ignore'.
                             """)

        return cls(byte_string.decode(encoding, errors=errors))

    def format(self, *args, **kwargs):
        # type: (*Any, **Any) -> ww.s.StringWrapper
        """ Like str.format(), with f-string features. Returns StringWrapper

            s().format() is like str.format() (or unicode.format() in
            Python 2.7), but returns a StringWrapper.

            However, if you don't pass any argument to it, it will act like
            f-strings, and look for the variables from the current local
            context to fill in the markers.

            Args:

                *args: elements used to replace {} markers.
                **kwargs: named element used to replace {name} markers.

            Returns:
                The formatted string, wrapped in StringWrapper

            Example:

                >>> from ww import s
                >>> print(s('Dis ize me, {} !').format('Mario'))
                Dis ize me, Mario !
                >>> name = 'Mario'
                >>> print(s('Dis ize me, {name} !').format())
                Dis ize me, Mario !
        """
        # TODO: check that globals are accessible
        if not args and not kwargs:
            pframe = inspect.currentframe().f_back
            return self.__class__(unicode.format(self, **pframe.f_locals))
        return self.__class__(unicode.format(self, *args, **kwargs))

    # TODO: i18n
    # todo: rename to 'as_bool'
    def to_bool(self, default=None):
        # type: (Any) -> bool
        """ Take a string with a binary meaning, and turn it into a boolean.

            The following strings will be converted:

                - '1' => True,
                - '0' => False,
                - 'true' => True,
                - 'false' => False,
                - 'on' => True,
                - 'off' => False,
                - 'yes' => True,
                - 'no' => False,
                - '' => False

            Args:

                default: the value to return if the string can't be
                         converted.

            Returns:
                A boolean matching the meaning of the string.

            Example:

                >>> from ww import s
                >>> s('true').to_bool()
                True
                >>> s('Off').to_bool()
                False
        """
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
            }[self.lower()]  # TODO: normalize + strip()
        except KeyError:
            if default is not None:
                return default
            raise ValueError(ww.f >> """
                             '{self!r}' cannot be converted to a boolean. Clean
                             your input or set the 'default' parameter to True
                             or False.
                             """)

    # TODO: decide if we test all those no cover
    if six.PY3:  # pragma: no cover
        def __repr__(self):
            """ Strings repr always prefixeds with 'u' even in Python 3 """
            return 'u{}'.format(super(StringWrapper, self).__repr__())


# TODO: make sure each class call self._class instead of s(), g(), etc
class FStringWrapper(with_metaclass(MetaF)):  # type: ignore
    """
        Factory to create StringWrapper objects, but with f-string like
        capabilities.

        Usage::

            >>> from ww import f  # or from ww import FStringWrapper
            >>> name = 'Foo'
            >>> type(f('My name is {name}'))
            <class 'ww.wrappers.strings.StringWrapper'>
            >>> print(f('My name is {name}'))
            My name is Foo
            >>> print(f >> '''
            ...     Dedent also works.
            ...     See: {name}
            ... ''')
            <BLANKLINE>
            Dedent also works.
            See: Foo
            <BLANKLINE>

        Since it returns a Strings wrapper, you can then look up s()
        documentation for the rest of what you can do.

        .. warning::

           Remember that, while f-strings are interpreted at parsing time,
           our implementation is executed at run-time, making it vulnerable
           to code injection. This makes it a dangerous feature to put
           in production.
    """
    def __new__(cls, string):
        # type: (str) -> StringWrapper
        """ Create a new s() object, formating it using the current context.

            Args:

                string: the string format.

            Returns:
                A formatted StringWrapper instance.

            Example:

                >>> from ww import f
                >>> name = 'Foo'
                >>> print(f('My name is {name}'))
                My name is Foo
        """
        caller_frame = inspect.currentframe().f_back
        caller_globals = caller_frame.f_globals
        caller_locals = caller_frame.f_locals
        return StringWrapper(FORMATTER.format(string, caller_globals,
                                              caller_locals))
