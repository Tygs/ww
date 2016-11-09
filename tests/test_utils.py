
import pytest

from ww.utils import require_positive_number, renamed_argument


def test_require_positive_number():

    assert require_positive_number('1', 'foo') == 1
    assert require_positive_number(1.1, 'foo') == 1

    with pytest.raises(ValueError):
        require_positive_number('a', 'foo')

    with pytest.raises(ValueError):
        require_positive_number(-1, 'foo')


def test_renamed_argument():

    @renamed_argument('old_bar', 'bar')
    def foo(bar):
        return 1

    assert foo(bar=1) == 1

    with pytest.raises(TypeError):
        foo(old_bar=1)
