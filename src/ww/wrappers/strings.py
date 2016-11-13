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
            ...
            ... Because clean_spaces() remove uneeded spaces.
            ... ''').clean_spaces())
            This should be over indented. But it will not be.
            <BLANKLINE>
            Because clean_spaces() remove uneeded spaces.

        By overriding operators, we can provide some interesting syntaxic
        sugar, such as this shortcut for writting long dedented text::

            >>> print(s >> '''
            ... Calling clean_spaces() is overrated.
            ...
            ... Overriding __rshift__ is much more fun.
            ... ''')
            Calling clean_spaces() is overrated.
            <BLANKLINE>
            Overriding __rshift__ is much more fun.

        Also we hacked something that looks like Python 3.6 f-string, but
        that works in Python 2.7 and 3.3+:

            >>> from ww import f
            >>> a = 1
            >>> f('Sweet, I can print locals: {a}')
            u'Sweet, I can print locals: 1'
            >>> print(f >> '''
            ... Yes it works with long string too.
            ...
            ... And globals, if you are into that kind
            ... of things.
            ...
            ... But we have only {a} for now.
            ... ''')
            Yes it works with long string too.
            <BLANKLINE>
            And globals, if you are into that kind of things.
            <BLANKLINE>
            But we have only 1 for now.

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

# TODO: 'partition', rsplit, splitlines
# TODO : flags can be passed as strings. Ex: s.search('regex', flags='ig')
# TODO : make s.search(regex) return a wrapper with __bool__ evaluating to
# false if no match instead of None and allow default value for group(x)
# also allow match[1] to return group(1) and match['foo'] to return
# groupdict['foo']
# TODO .groups would be a g() object
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
import textwrap

from ww.utils import wraps

import six
import chardet

from six import with_metaclass
from future.utils import bind_method
from future.utils import raise_from

try:
    from formatizer import LiteralFormatter
    FORMATTER = LiteralFormatter()
except ImportError:  # pragma: no cover
    FORMATTER = str

import ww
from ww.tools.strings import (multisplit, multireplace, casefold, map_format,
                              make_translation_table, translate_caracters)
from ww.utils import renamed_argument
from ww.types import (Union, unicode, str_istr, str_istr_icallable,  # noqa
                      C, I, Iterable, Callable, Any)

FORMATTER = LiteralFormatter()

# List of methods returning unicode strings that we want to automatically
# convert to return StringWrapper. We plug them in a loop at the end
# of this file, but before we make sure the method exist on
# the current unicode object
AUTO_METHODS = {'capitalize', 'center', 'expandtabs', 'ljust', 'lower',
                'lstrip', 'rjust', 'rstrip', 'swapcase', 'title', 'upper',
                'zfill', 'strip'} & set(dir(unicode))


class MetaS(type):
    """ Allow s >> 'text' as a shortcut to apply clean_spaces() to strings.

        This is not something you should use directly. It's a metaclass
        for StringWrapper objects and is used to override the
        operator >> on the StringWrapper class (not the object).
    """

    def __rshift__(self, other):
        # type (str) -> StringWrapper
        """ Allow s >> "a string" as a shortcut to s("a string").clean_spaces()

            s is the class, not s(), which would be an instance.

            Args:
                other: the string at the right of the '>>' operator.

            Returns:
                clean_spaces(string), wrapped in StringWrapper. Right now
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
                This should be indented but it will not be
        """
        # TODO: figure out how to allow this to work with subclasses
        return StringWrapper(ww.tools.strings.clean_spaces(other))


class MetaF(type):
    """ Allow f >> 'text' as a shortcut to clean_spaces() for f-like-strings.

        This is not something you should use directly. It's a metaclass
        for s() StringWrapper objects and is used to override the
        operator >> on the StringWrapper class (not the object).

        This is the same as MetaS, but it wraps the string in f(), not in
        s(), meaning you can use the f-string compatible syntax inside
        the string you wish to apply clean_spaces() to.

        .. warning::

           Remember that, while f-strings are interpreted at parsing time,
           our implementation is executed at run-time, making it vulnerable
           to code injection. This makes it a dangerous feature to put in
           production.
    """

    def __rshift__(self, other):
        # type (str) -> StringWrapper
        """ Allow f >> "a string" as a shortcut to f("a string").clean_spaces()

            f is the class, not f(), which would be an instance.

            Args:
                other: the string at the right of the '>>' operator.

            Returns:
                clean_spaces(string) and wrapped in StringWrapper. Right now
                we always return StringWrapper, so subclassing won't work
                if you want to override this.

            Raises:
                TypeError: if you try to apply it on non strings.

            Example:

                >>> from ww import f
                >>> var = "foo"
                >>> print(f >> '''
                ...     It should be indented
                ...     but it will not be.
                ...     And you can use {var}.
                ... ''')
                It should be indented but it will not be. And you can use foo.

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
        return StringWrapper(
            FORMATTER.format(other, caller_globals, caller_locals)
        ).clean_spaces()


# TODO: add normalize() (removes special caracters) and slugify
# (normalize + slug)
# TODO: refactor methods to be only wrappers
#       for functions from a separate module
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
        return self.__class__(textwrap.dedent(self))

    def unbreak(self):
        # type: (...) -> StringWrapper
        r""" Remove lone line breaks.

            A lone line break is a line break not next to another line break.

            Lone lines breaks at the begining or at the end are removed. Any
            others are replaced with a space.

            Returns:
                The strings with lone line breaks removed, wrapped
                in StringWrapper.

            Example:

                >>> from ww import s
                >>> print(s('''It should have line breaks
                ... but it will not.
                ... ''').unbreak())
                It should have line breaks but it will not.
                >>> print(s('''Multiple line breaks are not stripped.
                ...
                ... So you can create paragraphes by breaking
                ... twice.''').unbreak())
                Multiple line breaks are not stripped.
                <BLANKLINE>
                So you can create paragraphes by breaking twice.
        """
        return self.__class__(ww.tools.strings.unbreak(self))

    def clean_spaces(self):
        # type: (...) -> StringWrapper
        r""" Remove unecessary string indentations, spaces and linebreaks.

            This is espacially useful when you have long strings
            that you wish to break other several lines but don't want it
            to be indented or have line breaks. E.G: exception messages.

            You can use the f >> or s >> as shortcuts to this method.

            Returns:
                The strings without unecessary indentation, with both ends
                striped of unprintable caracters with lone line breaks removed.

            Example:

                >>> from ww import s
                >>> print(s('''
                ...     It should be indented and with a line break
                ...     but it will not be.
                ... ''').clean_spaces())
                It should be indented and with a line break but it will not be.
                >>> print(s('''
                ...     Multiple line breaks are not stripped.
                ...
                ...     So you can create paragraphes by breaking
                ...     twice. Also:
                ...
                ...         Desired indentation is not removed.
                ...
                ... ''').clean_spaces())
                Multiple line breaks are not stripped.
                <BLANKLINE>
                So you can create paragraphes by breaking twice. Also:
                <BLANKLINE>
                    Desired indentation is not removed.
                >>> print(s >> '''
                ...     s() implements >> as a shorcut to
                ...     s(string).clean_spaces().
                ... ''')  # shortcut version
                s() implements >> as a shorcut to s(string).clean_spaces().
        """
        return self.__class__(ww.tools.strings.clean_spaces(self))

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

    def casefold(self):
        # type: (...) -> StringWrapper
        u""" Make the string lower case, even with unicode caracters.

            s.lower() works with ASCII caracters only. s.casefold() will
            work on unicode caracters. Python 2 doesn't have unicode.casefold()
            but s.casefold() works with all supported versions.

            Returns:
                A lower case strings, wrapped in StringWrapper.

            Example:

                >>> from ww import s
                >>> s("AbCd").casefold() == s("AbCd").lower() == "abcd"
                True
                >>> folded = s(u"ΣίσυφοςﬁÆ").casefold()
                >>> print(folded, ':', len(folded))
                σίσυφοσfiæ : 10
                >>> lowercased = s(u"ΣίσυφοςﬁÆ").lower()
                >>> print(lowercased, ':', len(lowercased))
                σίσυφοςﬁæ : 9
        """
        return self.__class__(casefold(self))

    @classmethod
    @renamed_argument(('x', 'frm', 'to', 'y', 'z'),
                      ('caracters', 'caracters',
                       'substitutions', 'substitutions',
                       'to_delete'))
    def maketrans(cls, caracters, substitutions=None, to_delete=None):
        # type: (Union[str, dict], str, str) -> ww.d
        """ Create a dictionary containing caracters and their replacements

            This is the same as Python 3's str.maketrans (minus the argument
            names) and similar to Python 2 string.maketrans. The goal is to
            create a dict you can pass to s.translate to replace caracters
            by others or remove caracters.

            You can build this dictionary by hand, maketrans is just a shortcut
            to do it.

            Args:
                caracters: A string containing all the caracters you want to
                           replace. Or a dictionary with the keys being the
                           caracters you want to replace, and the value the
                           caracters to replace them with.
                substitutions: a string containing all the caracters you want
                               to use as replacements. This string must be of
                               the same length of the string you used
                               in the `caracters` parameters.
                               One exception: you can pass an empty string or a
                               single carater to replace all caracters from
                               `caracters` with it.
                               If you passed a dict as `caracters`, don't use
                               `substitutions`.
                to_delete: A string containing caracters to remove. This will
                           map the caracters to None, and is an alternative to
                           passing an empty string in `substitutions`. This
                           is essentially to keep the compatibility with the
                           Python 3 maketrans signature.

            Returns:
                A DictWrapper mapping caracters to be replace with their
                replacements.

            Example:

                >>> from ww import s
                >>> s.maketrans(u'abc', u'xyw') # doctest: +ALLOW_UNICODE
                {97: u'x', 98: u'y', 99: u'w'}
                >>> s.maketrans(u'abc', u'')
                {97: None, 98: None, 99: None}
                >>> s.maketrans(u'abc', u'z') # doctest: +ALLOW_UNICODE
                {97: u'z', 98: u'z', 99: u'z'}
                >>> s.maketrans({u'a': u"x", u"b": u"y"}) # doctest: +ALLOW_UNICODE
                {97: u'x', 98: u'y'}
                >>> s.maketrans(u'abc', u'xyw', u'z') # doctest: +ALLOW_UNICODE
                {97: u'x', 98: u'y', 99: u'w', 122: None}

        """  # noqa
        table = ww.d()
        table.update(make_translation_table(caracters, substitutions))
        if to_delete is not None:
            if not isinstance(to_delete, unicode):
                raise TypeError(ww.f >> """
                    "to_delete" must be a unicode string. You passed
                    {to_delete} of type {type(to_delete)}
                """)
            table.update(make_translation_table(to_delete, ''))
        return table

    @renamed_argument('table', 'caracters')
    def translate(self, caracters, substitutions=None):
        # type: (Union[str, dict], str) -> StringWrapper
        """ Do a caracter by caracter substitution in the string

            Like unicode.translate(). Allow passing a translation table as
            usual (built manually or with s.maketrans()), but also
            alternatively passing caracters to build the translation table
            on the fly. The later is handy if you need it only once.

            You may want to use it instead of s.replace() as it will be
            faster, or if you already have something providing a mapping table,
            or for backward compatibility with some code using it.

            However, usually s.replace() is easier to use.

            Args:

                string: the string to apply the substitution on.
                caracters: either the translation table (a dict with the keys
                           being the ord() of the caracters to replace, and the
                           values being the replacements), or a string
                           containing the caracters to replace. In the later
                           case, those caracters will be used as the key of the
                           translation table.
                           If this is explicitly set to None, then the
                           caracters in `substitution` will be removed from the
                            string.
                substitutions: a string containing all the caracters you want
                               to use as replacements.
                               Use it conly if `caracters` is a string and
                               not a table, as this will be used as values to
                               build the translation table and
                               hence will be the replaccements for what's in
                               `caracters`.
                               This string must be of
                               the same length of the string you used
                               in the `caracters` parameters.
                               One exception: you can pass an empty string or a
                               single carater to replace all caracters from
                               `caracters` with it.

            Returns:
                A new string with caracters replaced, wrapped in
                StringWrapper.

            Example:

                >>> from ww import s
                >>> table = s.maketrans(u'abc', u'xyw')
                >>> table # doctest: +ALLOW_UNICODE
                {97: u'x', 98: u'y', 99: u'w'}
                >>> print(s(u'cat').translate(table))
                wxt
                >>> print(s(u'cat').translate(u'abc', u'xyw'))
                wxt
                >>> print(s(u'cat').translate(None, u'a'))
                ct
                >>> print(s(u'cat').translate(u'abc', u'z'))
                zzt
                >>> print(s(u'cat').translate(u'abc', u''))
                t
        """
        string = translate_caracters(self, caracters, substitutions)
        return self.__class__(string)

    def format_map(self, mapping):
        # type: (dict) -> StringWrapper
        """ Almost like unicode.format(**mapping).

            You will rarely need that, but it doesn't produce a new dictionary
            like s.format(**mapping) does, which means:

            - it's a bit faster;
            - you can pass a custom mapping with a specific behavior such as
              overriding __missing__.

            Args:
                string: the string to format, containing the markers.
                mapping: A mapping, such as a dict, with the keys being the
                         name of the markers, and the values being the value to
                         be inserted at the marker.

            Returns:
                A formatted string, wrapper in a StringWrapper.

            Example:

                >>> from ww import s
                >>> print(s("{foo}").format_map({"foo": "bar"}))
                bar
        """
        return self.__class__(map_format(self, mapping))

    # TODO: decide if we test all those "no cover"
    if six.PY3:  # pragma: no cover
        def __repr__(self):
            """ Strings repr always prefixeds with 'u' even in Python 3 """
            return 'u{}'.format(super(StringWrapper, self).__repr__())


# Add methods with the result being converted automatically to StringWrapper
for name in AUTO_METHODS:

    # Get the original unicode method, such as unicode.title, unicode.upper...
    method = getattr(unicode, name)

    # Use a factory to have a paramter with the same name as the local
    # variable and avoid a closure which would always reference the same
    # method
    def factory(method):

        # This wraps the original unicode method so it returns a StringWrapper
        @wraps(method)
        def wrapper(*args, **kwargs):
            # type(...) -> StringWrapper
            return StringWrapper(method(*args, **kwargs))

        return wrapper

    # Build the wrapper with the proper method passed as a reference
    wrapper = factory(method)

    # Make sure we have a docstring stating this is an automatic method, but
    # include the original docstring in it just in case.
    wrapper.__doc__ = str(StringWrapper(  # noqa
    """ Same as unicode.{name}(), but return a StringWrapper

    This method has been converted automatically, but the behavior is exactly
    the same than the original method, except we wrap the result in
    a StringWrapper.

    Here is the original docstring:

    '''
    {method.__doc__}
    '''
    """).format().dedent())

    # Attach our new method to s()
    bind_method(StringWrapper, name, wrapper)


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
            Dedent also works. See: Foo

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
