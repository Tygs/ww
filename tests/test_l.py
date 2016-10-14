from ww import l


def test_len():

    lst = l([1, 2, 3])

    assert lst.len == 3


def test_join():

    lst = l("012")
    assert lst.join(',', template="{}#") == "0#,1#,2#"
    assert lst.join(',') == "0,1,2"
    string = lst.join(',', formatter=lambda x, y: str(int(x) ** 2))
    assert string == "0,1,4"


def test_append():

    lst = l([])
    lst.append(1).append(2, 3).append(4, 5)

    assert lst == [1, 2, 3, 4, 5]


def test_extend():
    lst = l([])
    lst.extend([1, 2, 3]).extend([4, 5, 6])

    assert lst == [1, 2, 3, 4, 5, 6]
