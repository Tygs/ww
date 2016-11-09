import pytest
from ww import t
from ww import l
from ww import d


def test_len():
    tple = t((1, 2, 3))

    assert tple.len == 3


def test_index():
    tple = t(("un", "deux", "trois"))

    assert tple.index('un') == 0


def test_bad_index():
    tple = t(("un", "deux", "trois"))

    with pytest.raises(ValueError):
        tple.index('quatre')


def test_to_l_is_true():
    tple = t((1, 2, 3, 4))

    assert isinstance(tple.to_l(), type(l()))
    assert tple.to_l() == [1, 2, 3, 4]


def test_to_d():
    tple = t(((1, 2), (3, 4)))

    assert isinstance(tple.to_d(), type(d()))
    assert tple.to_d() == {1: 2, 3: 4}


def test_to_d_with_bad_input():
    tple = t(((1, 2), (3, 4), (5)))

    with pytest.raises(ValueError):
        tple.to_d()

    tple = t(((1, 2), (3, 4), (5, 6, 7)))

    with pytest.raises(ValueError):
        tple.to_d()

    tple = t((None, (1, 2), (3, 4)))

    with pytest.raises(ValueError):
        tple.to_d()

    def gen():
        yield (1, 2)
        raise TypeError('Foo')

    tple = t((gen(),))
    with pytest.raises(TypeError):
        tple.to_d()
