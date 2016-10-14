import math
import pytest

from ww import d


def test_add_():
    current_dict = d({1: 1, 2: 2, 3: 3})
    to_merge_dict = {3: 4, 4: 5}
    merged_dict = current_dict + to_merge_dict
    assert len(current_dict) == 3
    assert len(to_merge_dict) == 2
    assert len(merged_dict) == 4
    assert merged_dict[3] == 4
    assert merged_dict[4] == 5


def test_radd():
    current_dict = {1: 1, 2: 2, 3: 3}
    to_merge_dict = d({3: 4, 4: 5})
    merged_dict = current_dict + to_merge_dict
    assert len(current_dict) == 3
    assert len(to_merge_dict) == 2
    assert len(merged_dict) == 4
    assert merged_dict[3] == 4
    assert merged_dict[4] == 5


def test_isubset():
    curr_dict = d({1: 'abcd', 2: "azr"})
    g = curr_dict.isubset(1, 2)
    assert next(g) == (1, 'abcd')
    assert next(g) == (2, 'azr')
    with pytest.raises(StopIteration):
        list(next(g))


def test_isubset_unexisting_key():
    curr_dict = d({1: 'abcd', 2: "azr"})
    g = curr_dict.isubset('a')
    with pytest.raises(KeyError):
        list(next(g))


def test_subset():
    curr_dict = d({1: 'abcd', 2: "azr", 3: "ooo"})
    subset = curr_dict.subset(1, 3)
    assert len(subset) == 2
    assert 1 in subset
    assert 3 in subset
    assert 2 not in subset


def test_subset_unexisting_key():
    curr_dict = d({1: 'abcd', 2: "azr", 3: "ooo"})
    with pytest.raises(KeyError):
        curr_dict.subset(1, 4)


def test_swap():
    curr_dict = d({1: 'abcd', 2: "azr", 3: "ooo"})
    swapped = curr_dict.swap()
    assert swapped['abcd'] == 1
    assert swapped['azr'] == 2
    assert swapped['ooo'] == 3


def test_swap_duplicate():
    curr_dict = d({1: 'abcd', 2: "abcd", 3: "ooo"})
    swapped = curr_dict.swap()
    assert len(swapped) == 2
    assert swapped['abcd'] in [1, 2]
    assert swapped['ooo'] == 3


def test_add():
    curr_dict = d({1: 'abcd', 2: "abcd", 3: "ooo"})
    curr_dict.add(1, "azer").add(5, "mmm")
    assert len(curr_dict) == 4
    assert curr_dict[1] == "azer"
    assert curr_dict[5] == "mmm"


def test_iterator():
    curr_dict = d({1: 'abcd', 2: "abcd", 3: "ooo"})
    list_iterator = list(curr_dict)
    assert len(list_iterator) == 3
    assert (1, 'abcd') in list_iterator
    assert (2, 'abcd') in list_iterator
    assert (3, 'ooo') in list_iterator


def test_from_key_val():
    curr_dict = d.fromkeys(*'123', value=4)
    assert len(curr_dict) == 3
    assert curr_dict['1'] == 4
    assert curr_dict['2'] == 4
    assert curr_dict['3'] == 4


def test_from_key_lambda():
    curr_dict = d.fromkeys(*range(3), value=lambda v: v ** 2)
    assert len(curr_dict) == 3
    assert curr_dict[0] == 0
    assert curr_dict[1] == 1
    assert curr_dict[2] == 4


def test_from_key_call():
    curr_dict = d.fromkeys(*range(3), value=math.sqrt)
    assert len(curr_dict) == 3
    for i in range(3):
        assert curr_dict[i] == math.sqrt(i)


def test_merge():
    curr_dict = d({1: 'abcd', 2: "abcd", 3: "ooo"})
    to_merge = d({3: "ccc", 4: "hell"})
    curr_dict = curr_dict.merge(to_merge)
    assert len(curr_dict) == 4
    assert curr_dict[3] == "ccc"
    assert curr_dict[4] == "hell"


def test_delete():
    current_dict = d({1: 1, 2: 2, 3: 3})
    current_dict = current_dict.delete(*[1, 2, 5])
    assert len(current_dict) == 1
    assert current_dict[3] == 3
