
import re

import pytest

from ww import s, g

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
