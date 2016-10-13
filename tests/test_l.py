

from ww import l

def test_len():
    
    lst = l([1, 2, 3])
    
    assert lst.len == 3

def test_append():

    lst = l([])
    lst.append(1).append(2, 3).append(4,5)
    
    assert lst == [1, 2, 3, 4, 5]

def test_extend():
    lst = l([])
    lst.extend([1, 2, 3]).extend([4, 5, 6])
    
    assert lst == [1, 2, 3, 4, 5, 6]