# coding: utf-8

from __future__ import (
    unicode_literals, division, print_function, absolute_import
)

import re

import pytest

from ww import s, g, f
from ww.tools.strings import make_translation_table


def test_lshift():

    res = s >> """
    This is a long text
    And it's not indented
    """
    assert isinstance(res, s)

    s == "This is a long text\nAnd it's not indented"


def test_split():

    gen = s('test').split(',')
    assert isinstance(gen, g)
    assert gen.list() == ['test']

    assert s('test,test').split(',').list() == ['test', 'test']

    assert s('a,b,c').split(',', maxsplit=1).list() == ['a', 'b,c']

    assert s('a,b,c').split('b,').list() == ['a,', 'c']

    assert s('a,b;c/d').split(',', ';', '/').list() == ['a', 'b', 'c', 'd']

    assert s(r'a1b33c-d').split(r'\d+').list() == ['a', 'b', 'c-d']

    assert s(r'a1b33c-d').split(r'\d+', '-').list() == ['a', 'b', 'c', 'd']

    assert s(r'cAt').split('a', flags='i').list() == ['c', 't']

    assert s(r'cAt').split('a', flags=re.I).list() == ['c', 't']

    chunks = s('a,b;c/d=a,b;c/d').split(',', ';', '/', maxsplit=3)
    assert chunks.list() == ['a', 'b', 'c', 'd=a,b;c/d']

    with pytest.raises(TypeError):
        s('foo').split(1)


def test_maxsplit_with_regex():
    chunks = s('a,b;c/d=a,b;c/d').split(',', ';', '[/=]', maxsplit=4)
    assert chunks.list() == ['a', 'b', 'c', 'd', 'a,b;c/d']


def test_replace():

    st = s('test').replace(',', '')
    assert isinstance(st, s)
    assert st == 'test'

    assert s('test,test').replace(',', ';') == 'test;test'

    assert s('a,b,c').replace(',', ';', maxreplace=1) == 'a;b,c'

    assert s('a,b,c').replace(',b,', ';') == 'a;c'

    assert s('a,b;c/d').replace((',', ';', '/'), (',', ',', ',')) == 'a,b,c,d'

    assert s('a,b;c/d').replace((',', ';', '/'), ',') == 'a,b,c,d'

    assert s(r'a1b33c-d').replace(r'\d+', ',') == 'a,b,c-d'

    assert s(r'a1b33c-d').replace((r'\d+', '-'), ',') == 'a,b,c,d'

    assert s(r'cAt').replace('a', 'b', flags='i') == 'cbt'

    assert s(r'cAt').replace('a', 'b', flags=re.I) == 'cbt'

    with pytest.raises(ValueError):
        s(r'cAt').replace(('a', 'b', 'c'), ('b', 'b'))


def test_replace_with_maxplit():
    string = s(r'a-1,b-3,3c-d')
    assert string.replace(('[,-]'), '', maxreplace=3) == 'a1b3,3c-d'


def test_replace_with_callback():
    string = s(r'a-1,b-3,3c-d')

    def upper(match):
        return match.group().upper()

    assert string.replace(('[ab]'), upper, maxreplace=3) == 'A-1,B-3,3c-d'


def test_join():

    assert s(';').join('abc') == "a;b;c"
    assert s(';').join(range(3)) == "0;1;2"
    assert s(';').join(range(3), template="{:.1f}") == "0.0;1.0;2.0"
    assert s(';').join(range(3), formatter=lambda s, t: "a") == "a;a;a"


def test_from_bytes():

    assert isinstance(s.from_bytes(b'abc', 'ascii'), s)
    assert s.from_bytes(b'abc', 'ascii') == 'abc'

    assert s.from_bytes('é'.encode('utf8'), 'utf8') == 'é'

    with pytest.raises(UnicodeDecodeError):
        s.from_bytes('é'.encode('cp850'), 'ascii')

    with pytest.raises(ValueError):
        s.from_bytes('é'.encode('cp850'))


def test_format():

    foo = 1
    bar = [1]
    string = s('{foo} {bar[0]:.1f}')
    assert isinstance(string.format(foo=foo, bar=bar), s)
    assert string.format(foo=foo, bar=bar) == "1 1.0"

    assert string.format_map(dict(foo=foo, bar=bar)) == "1 1.0"

    assert f(string) == "1 1.0"
    assert isinstance(f(string), s)
    assert f('{foo} {bar[0]:.1f}') == "1 1.0"


def test_add():

    string = s('foo')
    assert string + 'bar' == 'foobar'

    with pytest.raises(TypeError):
        string + b'bar'

    with pytest.raises(TypeError):
        string + 1

    assert 'bar' + string == 'barfoo'

    with pytest.raises(TypeError):
        b'bar' + string

    with pytest.raises(TypeError):
        1 + string


def test_tobool():

    conversions = {
        '1': True,
        '0': False,
        'true': True,
        'false': False,
        'on': True,
        'off': False,
        'yes': True,
        'no': False,
        '': False
    }

    for key, val in conversions.items():
        assert s(key).to_bool() == val

    assert s('foo').to_bool(default=True) is True

    with pytest.raises(ValueError):
        s('foo').to_bool()


def test_unbreak():

    assert s('''
      a
      b

      c
    ''').unbreak() == "a b\n\n      c"


def test_clean_spaces():

    assert s('''
      a
      b

      c
    ''').clean_spaces() == "a b\n\nc"

    assert s >> '''
      a
      b

      c
    ''' == "a b\n\nc"


def test_capitalize():
    assert s('Foo bar').capitalize() == 'Foo bar'.capitalize()


def test_casefold():
    assert s("ΣίσυφοςﬁÆ").casefold() == "σίσυφοσfiæ"
    assert s("ΣΊΣΥΦΟσFIæ").casefold() == "σίσυφοσfiæ"


def test_simple_automethods():

    simple_auto_methods = ('capitalize', 'lower', 'upper', 'title',
                           'strip', 'lstrip', 'rstrip', 'swapcase',
                           'expandtabs')

    string = '    AbCd\t'
    sstring = s(string)
    for name in simple_auto_methods:
        sstring_method_result = getattr(sstring, name)()
        assert getattr(string, name)() == sstring_method_result
        assert isinstance(sstring_method_result, s)


def test_padding():

    padding_methods = ('center', 'rjust', 'ljust', 'zfill')

    string = 'abcd'
    sstring = s(string)
    for name in padding_methods:
        sstring_method_result = getattr(sstring, name)(10)
        assert getattr(string, name)(10) == sstring_method_result
        assert isinstance(sstring_method_result, s)


def test_translate():

    assert s.maketrans('abc', 'xyw') == {97: 'x', 98: 'y', 99: 'w'}
    assert s.maketrans('abc', '') == {97: None, 98: None, 99: None}
    assert s.maketrans('abc', 'z') == {97: 'z', 98: 'z', 99: 'z'}
    assert s.maketrans({'a': "x", "b": "y"}) == {97: 'x', 98: 'y'}
    assert s.maketrans('abc', 'xyw', 'z') == {97: 'x', 98: 'y',
                                              99: 'w', 122: None}

    with pytest.raises(ValueError):
        make_translation_table(1)

    table = s.maketrans('abc', 'xyw')
    assert s('cat').translate(table) == 'wxt'
    assert s('cat').translate('abc', 'xyw') == 'wxt'
    assert s('cat').translate(None, 'a') == 'ct'
    assert s('cat').translate('abc', 'z') == 'zzt'
    assert s('cat').translate('abc', '') == 't'
