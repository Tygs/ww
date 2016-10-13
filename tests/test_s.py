# coding: utf-8
from __future__ import (
    unicode_literals, division, print_function, absolute_import
)
import re

import pytest

from ww import s, g, f


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

    assert s(r'a1b33c-d').split('\d+').list() == ['a', 'b', 'c-d']

    assert s(r'a1b33c-d').split('\d+', '-').list() == ['a', 'b', 'c', 'd']

    assert s(r'cAt').split('a', flags='i').list() == ['c', 't']

    assert s(r'cAt').split('a', flags=re.I).list() == ['c', 't']


def test_replace():

    st = s('test').replace(',', '')
    assert isinstance(st, s)
    assert st == 'test'

    assert s('test,test').replace(',', ';') == 'test;test'

    assert s('a,b,c').replace(',', ';', maxreplace=1) == 'a;b,c'

    assert s('a,b,c').replace(',b,', ';') == 'a;c'

    assert s('a,b;c/d').replace((',', ';', '/'), (',', ',', ',')) == 'a,b,c,d'

    assert s('a,b;c/d').replace((',', ';', '/'), ',') == 'a,b,c,d'

    assert s(r'a1b33c-d').replace('\d+', ',') == 'a,b,c-d'

    assert s(r'a1b33c-d').replace(('\d+', '-'), ',') == 'a,b,c,d'

    assert s(r'cAt').replace('a', 'b', flags='i') == 'cbt'

    assert s(r'cAt').replace('a', 'b', flags=re.I) == 'cbt'


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

    assert f(string) == "1 1.0"
    assert isinstance(f(string), s)
    assert f('{foo} {bar[0]:.1f}') == "1 1.0"
