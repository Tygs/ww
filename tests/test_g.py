# coding: utf-8

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)


import pytest

from ww import g


def test_iter():

    for i, x in enumerate(g('abcd')):
        assert x == 'abcd'[i]

    for i, x in enumerate(g(list('abcd'))):
        assert x == 'abcd'[i]

    for i, x in enumerate(g(tuple('abcd'))):
        assert x == 'abcd'[i]

    assert set(g(set('abcd'))) == set('abcd')

    for i, x in enumerate(g(range(10))):
        assert x == i

    def foo():
        yield 0
        yield 1
        yield 2

    for i, x in enumerate(g(foo())):
        assert x == i


def test_nested():
    for i, x in enumerate(g(g(g('abcd')))):
        assert x == 'abcd'[i]


def test_accept_multi_iterables():

    numbers = list(map(int, g([1, 2, 3], '456', range(7, 10))))
    assert numbers == list(range(1, 10))


def test_next():

    gen = g('abc')
    assert next(gen) == 'a'
    assert gen.next() == 'b'


def test_add():

    gen = g('abc') + 'def'
    assert isinstance(gen, g)
    assert list(gen) == list('abcdef')

    gen = 'abc' + g('def')
    assert isinstance(gen, g)
    assert list(gen) == list('abcdef')


def test_sub():

    gen = g('abcdef') - list('ac')
    assert isinstance(gen, g)
    assert list(gen) == list('bdef')

    gen = g(['aa', 'ab', 'ac']) - 'ac'
    assert list(gen) == ['aa', 'ab']

    gen = 'abcdef' - g('ac')
    assert isinstance(gen, g)
    assert list(gen) == list('bdef')


def test_mul():

    gen = g(range(3)) * 3
    assert isinstance(gen, g)
    assert list(gen) == [0, 1, 2, 0, 1, 2, 0, 1, 2]

    gen = 2 * g(range(3))
    assert isinstance(gen, g)
    assert list(gen) == [0, 1, 2, 0, 1, 2]


def test_tee():

    gen = g(x * x for x in range(3))
    gen2, gen3 = gen.tee()

    assert list(gen2) == list(gen3) == [0, 1, 4]

    gen = g(x * x for x in range(3))
    all_gens = gen.tee(3)
    assert isinstance(all_gens, g)

    for x in all_gens:
        assert isinstance(x, g)
        assert list(x) == [0, 1, 4]

    gen = g(x * x for x in range(3))
    gen2, gen3 = gen.tee()

    with pytest.raises(RuntimeError):
        list(gen)


def test_getitem():

    gen = g(x * x for x in range(10))
    assert isinstance(gen[3:5], g)

    assert list(gen[3:8]) == [9, 16, 25, 36, 49]

    assert g(x * x for x in range(10))[3] == 9

    def ends_with_5(x):
        return str(x).endswith('5')
    gen = g(x * x for x in range(10))
    assert gen[ends_with_5:].list() == [25, 36, 49, 64, 81]

    assert g(x * x for x in range(10))[ends_with_5] == 25

    gen = g(x * x for x in range(10))
    assert gen[:ends_with_5].list() == [0, 1, 4, 9, 16]

    gen = g(x * x for x in range(10))
    assert gen[2:ends_with_5].list() == [4, 9, 16]

    gen = g(x * x for x in range(10))
    assert gen[ends_with_5:8].list() == [25, 36, 49]

    assert g(x * x for x in range(10))[-1] == 81

    with pytest.raises(ValueError):
        assert gen["not a callable"]


def test_map():

    gen = g("123").map(int)
    assert isinstance(gen, g)
    assert list(gen) == [1, 2, 3]


def test_zip():

    gen = g("123").zip("abc")
    assert isinstance(gen, g)
    assert list(gen) == list(zip("123", "abc"))

    gen = g("123").zip("abc", (True, False, None))
    assert isinstance(gen, g)
    assert list(gen) == list(zip("123", "abc", (True, False, None)))

def test_cycle():

    gen = g("12").cycle()
    assert isinstance(gen, g)

    assert next(gen) == "1"
    assert next(gen) == "2"
    assert next(gen) == "1"
    assert next(gen) == "2"
    assert next(gen) == "1"
    assert next(gen) == "2"


def test_chunks():

    gen = g('123456789').chunks(3)
    assert isinstance(gen, g)
    assert list(gen) == [('1', '2', '3'), ('4', '5', '6'), ('7', '8', '9')]

    gen = g('123456789').chunks(2, list)
    assert isinstance(gen, g)
    assert list(gen) == [['1', '2'], ['3', '4'], ['5', '6'], ['7', '8'], ['9']]


def test_window():

    gen = g('12345').window(3)
    assert isinstance(gen, g)
    assert list(gen) == [('1', '2', '3'), ('2', '3', '4'), ('3', '4', '5')]

    gen = g('12345').window(2, list)
    assert isinstance(gen, g)
    assert list(gen) == [['1', '2'], ['2', '3'], ['3', '4'], ['4', '5']]


def test_chaining_calls():

    gen = (g("0123456") + g("789") - "2")[:5].map(int).chunks(3)
    assert isinstance(gen, g)
    assert list(gen) == [(0, 1, 3), (4, 5)]


def test_groupby():

    data = [(1, True), (2, True), (3, True), (4, False), (5, False), (6, True)]
    gen = g(data).groupby(lambda x: x[1])
    assert isinstance(gen, g)
    assert list(gen) == [(False, ((4, False), (5, False))),
                        (True, ((1, True), (2, True), (3, True), (6, True)))]

    gen = g(data).groupby(lambda x: x[1], reverse=True)
    assert list(gen) == [(True, ((1, True), (2, True), (3, True), (6, True))),
                         (False, ((4, False), (5, False)))]

    gen = g('yyuiyuiyiyuyi').groupby(cast=lambda x: len(tuple(x)))
    assert list(gen) == [('i', 4), ('u', 3), ('y', 6)]


def test_firsts():

    gen = g("12345").firsts()
    assert isinstance(gen, g)

    a, = gen
    assert a == "1"

    a, b = g("12345").firsts(2)
    assert a == "1"
    assert b == "2"

    a, b, c = g("12").firsts(3)
    assert a == "1"
    assert b == "2"
    assert c is None

    a, b, c, d = g("12").firsts(4, default="other")
    assert a == "1"
    assert b == "2"
    assert c == d == "other"

    gen = g(range(5))
    a, b = gen.firsts(2)
    assert list(gen) == [2, 3, 4]


def test_lasts():

    gen = g("12345").lasts()
    assert isinstance(gen, g)

    a, = gen
    assert a == "5"

    a, b = g("12345").lasts(2)
    assert a == "4"
    assert b == "5"

    a, b, c = g("12").lasts(3)
    assert a == None
    assert b == "1"
    assert c is "2"

    a, b, c, d = g("12").lasts(4, default="other")
    assert a == b == "other"
    assert c == "1"
    assert d == "2"

    gen = g(range(5))
    a, b = gen.lasts(2)
    assert list(gen) == []


def test_skip_duplicates():

    gen = g("12345").skip_duplicates()
    assert isinstance(gen, g)

    gen = g("12345").skip_duplicates()
    assert list(gen) == ["1", "2", "3", "4", "5"]

    gen = g("123333333322234").skip_duplicates()
    assert list(gen) == ["1", "2", "3", '4']

    gen = g([-1, 1, 2, 3]).skip_duplicates(key=abs)
    assert list(gen) == [-1, 2, 3]

    with pytest.raises(TypeError):
        list(g([{}, {}]).skip_duplicates())

    gen = g([1]).skip_duplicates(fingerprints=set([1]))
    assert list(gen) == []


def test_join():

    assert g(range(3)).join(',') == "0,1,2"
    assert g(range(3)).join(',', template="{}#") == "0#,1#,2#"
    string = g(range(3)).join(',', formatter=lambda x, y: str(x * x))
    assert string == "0,1,4"
