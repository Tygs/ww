# coding: utf-8

"""
    :doc:`s() </string_wrapper>` is very convenient, but it's only a
    thin wrapper on top of regular strings and the tools from this module.

    So if you want to apply some of the goodies from it without having to
    turn your strings into StringWrapper objects, you can use the functions
    from this module directly.

    They don't accept bytes as an input. If you do so and it works, you must
    know it's not a supported behavior and may change in the future. Only
    pass:

    - unicode objects in Python 2;
    - str objects in Python 3.

    Example:

        >>> from ww.tools.strings import multisplit  # same as s().split()
        >>> string = u'a,b;c/d=a,b;c/d'
        >>> chunks = multisplit(string, u',', u';', u'[/=]', maxsplit=4)
        >>> for chunk in chunks: print(chunk)
        a
        b
        c
        d
        a,b;c/d

    You'll find bellow the detailed documentation for each functions of.
    Go have a look, there is some great stuff here!
"""

from __future__ import absolute_import, division, print_function

import re
import string
import textwrap

from past.builtins import basestring

import ww
from ww.utils import require_positive_number, ensure_tuple
from ww.types import Union, unicode, str_istr, str_istr_icallable, C, I  # noqa


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
except AttributeError:  # pragma: no cover
    pass


def parse_re_flags(flags):
    bflags = 0
    if isinstance(flags, basestring):
        for flag in flags:
            bflags |= REGEX_FLAGS[flag]

        return bflags

    return flags


try:
    from py2casefold import casefold
except ImportError:
    casefold = unicode.casefold

try:
    format_map = str.format_map
except AttributeError:  # pragma: no cover
    def format_map(to_format, mapping):
        """ Just a polyfill for the missing feature in Python 2 """
        return string.Formatter().vformat(to_format, None, mapping)


# kwargs allow compatibiliy with 2.7 and 3 since you can't use
# keyword-only arguments in python 2
# TODO: remove empty strings
def multisplit(string,  # type: unicode
               *separators,  # type: unicode
               **kwargs  # type: Union[unicode, C[..., I[unicode]]]
               ):  # type: (...) -> I
    """ Like unicode.split, but accept several separators and regexes

        Args:
            string: the string to split.
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
            cast: what to cast the result to

        Returns:
            An iterable of substrings.

        Raises:
            ValueError: if you pass a flag without separators.
            TypeError: if you pass something else than unicode strings.

        Example:

            >>> for word in multisplit(u'fat     black cat, big'): print(word)
            fat
            black
            cat,
            big
            >>> string = u'a,b;c/d=a,b;c/d'
            >>> chunks = multisplit(string, u',', u';', u'[/=]', maxsplit=4)
            >>> for chunk in chunks: print(chunk)
            a
            b
            c
            d
            a,b;c/d

    """

    cast = kwargs.pop('cast', list)
    flags = parse_re_flags(kwargs.get('flags', 0))
    # 0 means "no limit" for re.split
    maxsplit = require_positive_number(kwargs.get('maxsplit', 0),
                                       'maxsplit')

    # no separator means we use the default unicode.split behavior
    if not separators:
        if flags:
            raise ValueError(ww.s >> """
                             You can't pass flags without passing
                             a separator. Flags only have sense if
                             you split using a regex.
                            """)

        maxsplit = maxsplit or -1  # -1 means "no limit" for unicode.split
        return unicode.split(string, None, maxsplit)

    # Check that all separators are strings
    for i, sep in enumerate(separators):
        if not isinstance(sep, unicode):
            raise TypeError(ww.s >> """
                '{!r}', the separator at index '{}', is of type '{}'.
                multisplit() only accepts unicode strings.
            """.format(sep, i, type(sep)))

    # TODO: split let many empty strings in the result. Fix it.

    seps = list(separators)  # cast to list so we can slice it

    # simple code for when you need to split the whole string
    if maxsplit == 0:
        return cast(_split(string, seps, flags))

    # slow implementation with checks for recursive maxsplit
    return cast(_split_with_max(string, seps, maxsplit, flags))


def _split(string, separators, flags=0):
    try:
        sep = separators.pop()
    except IndexError:
        yield string
    else:
        # recursive split until we got the smallest chunks
        for chunk in re.split(sep, string, flags=flags):
            for item in _split(chunk, separators, flags=flags):
                yield item


def _split_with_max(string, separators, maxsplit, flags=0):

    try:
        sep = separators.pop()
    except IndexError:
        yield string
    else:

        while True:

            if maxsplit <= 0:
                yield string
                break

            # we split only in 2, then recursively head first to get the rest
            res = re.split(sep, string, maxsplit=1, flags=flags)

            if len(res) < 2:
                yield string
                # Nothing to split anymore, we never reached maxsplit but we
                # can exit anyway
                break

            head, tail = res

            chunks = _split_with_max(head, separators,
                                     maxsplit=maxsplit, flags=flags)

            for chunk in chunks:
                # remove chunks from maxsplit
                yield chunk
                maxsplit -= 1

            string = tail


def multireplace(string,  # type: unicode
                 patterns,  # type: str_or_str_iterable
                 substitutions,  # type: str_istr_icallable
                 maxreplace=0,  # type: int
                 flags=0  # type: unicode
                 ):  # type: (...) -> bool
    """ Like unicode.replace() but accept several substitutions and regexes

        Args:
            string: the string to split on.
            patterns: a string, or an iterable of strings to be replaced.
            substitutions: a string or an iterable of string to use as a
                           replacement. You can pass either one string, or
                           an iterable containing the same number of
                           sustitutions that you passed as patterns. You can
                           also pass a callable instead of a string. It
                           should expact a match object as a parameter.
            maxreplace: the max number of replacement to make. 0 is no limit,
                        which is the default.
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
            The string with replaced bits.

        Raises:
            ValueError: if you pass the wrong number of substitution.

        Example:

            >>> print(multireplace(u'a,b;c/d', (u',', u';', u'/'), u','))
            a,b,c,d
            >>> print(multireplace(u'a1b33c-d', u'\d+', u','))
            a,b,c-d
            >>> print(multireplace(u'a-1,b-3,3c-d', u',|-', u'', maxreplace=3))
            a1b3,3c-d
            >>> def upper(match):
            ...     return match.group().upper()
            ...
            >>> print(multireplace(u'a-1,b-3,3c-d', u'[ab]', upper))
            A-1,B-3,3c-d
    """

    # we can pass either a string or an iterable of strings
    patterns = ensure_tuple(patterns)
    substitutions = ensure_tuple(substitutions)

    # you can either have:
    # - many patterns, one substitution
    # - many patterns, exactly as many substitutions
    # anything else is an error
    num_of_subs = len(substitutions)
    num_of_patterns = len(patterns)

    if num_of_subs == 1 and num_of_patterns > 0:
        substitutions *= num_of_patterns
    elif len(patterns) != num_of_subs:
            raise ValueError("You must have exactly one substitution "
                             "for each pattern or only one substitution")

    flags = parse_re_flags(flags)

    # no limit for replacing, use a simple code
    if not maxreplace:
        for pattern, sub in zip(patterns, substitutions):
            string, count = re.subn(pattern, sub, string, flags=flags)
        return string

    # ensure we respect the max number of replace accross substitutions
    for pattern, sub in zip(patterns, substitutions):
        string, count = re.subn(pattern, sub, string,
                                count=maxreplace, flags=flags)
        maxreplace -= count
        if maxreplace == 0:
            break

    return string


def unbreak(string):
    # type: (str) -> str
    r""" Remove lone line breaks.

        A lone line break is a line break not next to another line break.

        Lone lines breaks at the begining or at the end are removed. Any others
        are replaced with a space.

        Returns:
            The strings with lone line breaks removed.

        Example:

            >>> from ww.tools.strings import unbreak
            >>> print(unbreak('''It should have line breaks
            ... but it will not.
            ... '''))
            It should have line breaks but it will not.
            >>> print(unbreak('''Multiple line breaks are not stripped.
            ...
            ... So you can create paragraphes by breaking
            ... twice.'''))
            Multiple line breaks are not stripped.
            <BLANKLINE>
            So you can create paragraphes by breaking twice.
    """
    # Remove lone line break at the begining
    string = re.sub(r'^[ \t]*\n[ \t]*(?!\n)', '', string)

    # Remove lone line break at the end
    string = re.sub(r'(?<!\n)[ \t]*\n[ \t]*$', '', string)

    # Remplace line line breaks anywhere esle with a space
    return re.sub(r'(?<!\n)[ \t]*\n[ \t]*(?!\n)', ' ', string)


def clean_spaces(string):
    # type: (str) -> str
    r""" Remove unecessary string indentations, spaces and linebreaks.

        Apply unicode.strip(), textwrap.dedent() and ww.tools.string.unbreak().

        Args:
            string: The string to clean.

        Returns:
            The strings without unecessary indentation, with both ends
            striped of unprintable caracters with lone line breaks removed.

        Example:

            >>> from ww.tools.strings import clean_spaces
            >>> print(clean_spaces('''
            ...     It should be indented and with a line break
            ...     but it will not be.
            ... '''))
            It should be indented and with a line break but it will not be.
            >>> print(clean_spaces('''
            ...     Multiple line breaks are not stripped.
            ...
            ...     So you can create paragraphes by breaking
            ...     twice. Also:
            ...
            ...         Desired indentation is not removed.
            ...
            ... '''))
            Multiple line breaks are not stripped.
            <BLANKLINE>
            So you can create paragraphes by breaking twice. Also:
            <BLANKLINE>
                Desired indentation is not removed.
    """
    return unbreak(textwrap.dedent(string).strip())


def make_translation_table(caracters, substitutions=None):
    # type: (Union[str, dict], str) -> dict
    u""" Create a dictionary containing caracters and their replacements

        This is the simlar to Python 3's str.maketrans, and Python 2
        string.maketrans. The goal is to create a dict you can pass to
        unicode.translate to replace caracters by others or remove caracters.

        You can build this dictionary by hand, make_translation_table is
        just a shortcut to do it.

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

        Returns:
            A dict mapping caracters to be replace with their replacements.

        Example:

            >>> from ww.tools.strings import make_translation_table
            >>> make_translation_table(u'abc', u'xyw') # doctest: +ALLOW_UNICODE
            {97: u'x', 98: u'y', 99: u'w'}
            >>> make_translation_table(u'abc', u'')
            {97: None, 98: None, 99: None}
            >>> make_translation_table(u'abc', u'z') # doctest: +ALLOW_UNICODE
            {97: u'z', 98: u'z', 99: u'z'}
            >>> make_translation_table({u'a': u"x", u"b": u"y"}) # doctest: +ALLOW_UNICODE
            {97: u'x', 98: u'y'}
    """  # noqa
    if isinstance(caracters, unicode):
        if substitutions is None:
            raise ValueError(ww.f >> """
                If you pass a string for "caracters", you need to pass
                "substitutions".
            """)

        caracters_ord = (ord(char) for char in caracters)
        if substitutions == "":
            return dict.fromkeys(caracters_ord)  # type: ignore

        if len(substitutions) == 1:
            return dict(zip(caracters_ord, substitutions * len(caracters)))

        if len(substitutions) != len(caracters):
            raise ValueError(ww.f >> """
                The string you passed for 'caracters' has {len(caracters)}
                caracters while the string you passed for 'substitutions' has
                {len(substitutions)} caracters. They must be the same length.
            """)

        return dict(zip(caracters_ord, substitutions))

    try:
        return dict((ord(k), v) for k, v in caracters.items())  # type: ignore
    except (AttributeError):
        raise ValueError(ww.f >> """
            You passed "{caracters}" as value for the "caracters", which is not
            a string or a dictionary compatible type.
        """)


def translate_caracters(string, caracters, substitutions=None):
    # type: (str, Union[str, dict], str) -> str
    u""" Do a caracter by caracter substitution in the string

        Like unicode.translate(). Allow passing a translation table as usual
        (built manually or with make_translation_table()), but
        also alternatively passing caracters to build the translation table
        on the fly. The last one is handy if you need it only once.

        You may want to use it instead of multireplace() as it will be faster,
        or if you already have something providing a mapping table, or
        for backward compatibility with some code using it.

        However, usually multireplace is easier to use.

        Args:
            string: the string to apply the substitution on.
            caracters: either the translation table (a dict with the keys
                       being the ord() of the caracters to replace, and the
                       values being the replacements), or a string containing
                       the caracters to replace. In the later case,
                       those caracters will be used as the key of the
                       translation table.
                       If this is explicitly set to None, then the caracters in
                       `substitution` will be removed from the string.
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
            A new string with caracters replaced.

        Example:

            >>> from ww.tools.strings import translate_caracters
            >>> from ww.tools.strings import make_translation_table
            >>> table = make_translation_table(u'abc', u'xyw')
            >>> table  # doctest: +ALLOW_UNICODE
            {97: u'x', 98: u'y', 99: u'w'}
            >>> print(translate_caracters(u'cat', table))
            wxt
            >>> print(translate_caracters(u'cat', u'abc', u'xyw'))
            wxt
            >>> print(translate_caracters(u'cat', None, u'a'))
            ct
            >>> print(translate_caracters(u'cat', u'abc', u'z'))
            zzt
            >>> print(translate_caracters(u'cat', u'abc', u''))
            t

    """

    # substitue caracters
    if caracters is None:

        if not substitutions or not isinstance(substitutions, unicode):
            raise ValueError(ww.f >> """
                If you pass None for "caracters", you need to pass a non
                empty unicode string for substitutions.
            """)

        caracters = make_translation_table(substitutions, '')

    elif isinstance(caracters, unicode):
        caracters = make_translation_table(caracters, substitutions)

    return unicode.translate(string, caracters)


def map_format(string, mapping):
    """ Almost like unicode.format(**mapping).

        You will rarely need that, but it doesn't produce a new dictionary
        like unicode.format(**mapping) does, which means:

        - it's a bit faster;
        - you can pass a custom mapping with a specific behavior such as
          overriding __missing__.

        Args:
            string: the string to format, containing the markers.
            mapping: A mapping, such as a dict, with the keys being the name
                     of the markers, and the values being the value to
                     be inserted at the marker.

        Returns:
            A formatted string.

        Example:

            >>> from ww.tools.strings import map_format
            >>> print(map_format("{foo}", {"foo": "bar"}))
            bar
    """
    return format_map(string, mapping)
