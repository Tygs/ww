

from past.builtins import unicode as past_unicode

try:
    unicode = unicode  # type: ignore
except NameError:
    unicode = str

from typing import (Union, Iterable, Callable, Any, TypeVar, Hashable,  # noqa
                    Generic, Iterator)

T = TypeVar('T')  # noqa
T2 = TypeVar('T2')  # noqa
C = TypeVar('C', bound=Callable)  # noqa
I = TypeVar('I', bound=Iterable)  # noqa
istr = Iterable[past_unicode]  # noqa
str_istr = Union[past_unicode, istr]  # noqa
str_or_callable = Union[past_unicode, Callable]  # noqa
str_istr_icallable = Union[past_unicode, Iterable[str_or_callable]]  # noqa
