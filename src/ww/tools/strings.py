# coding: utf-8

import re

from past.builtins import basestring

import ww
from ww.utils import require_positive_number, unicode


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


def parse_re_flags(flags):
    bflags = 0
    if isinstance(flags, basestring):
        for flag in flags:
            bflags |= REGEX_FLAGS[flag]

        return bflags

    return flags


# kwargs allow compatibiliy with 2.7 and 3 since you can't use
# keyword-only arguments in python 2
# TODO: remove empty strings
def multisplit(string, *separators, **kwargs):  # type: ignore
    # type: (*unicode, int, unicode) -> list[unicode]
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

        Example:

            >>> from ww import s
            >>> string = s('fat     black cat, big bad dog')
            >>> string.split().list()
            [u'fat', u'black', u'cat,', u'big', u'bad', u'dog']
    """

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
        return _split(string, seps, flags)

    # slow implementation with checks for recursive maxsplit
    return _split_with_max(string, seps, maxsplit, flags)


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
