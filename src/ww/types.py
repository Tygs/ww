

from past.builtins import unicode as past_unicode

try:
    unicode = unicode  # type: ignore
except NameError:
    unicode = str


from typing import (Union, Iterable, Callable, Any, TypeVar, Hashable,
                    Generic, Iterator)  # noqa
T = TypeVar('T')
T2 = TypeVar('T2')
C = TypeVar('C', bound=Callable)
I = TypeVar('I', bound=Iterable)
istr = Iterable[past_unicode]
str_istr = Union[past_unicode, istr]
str_or_callable = Union[past_unicode, Callable]
str_istr_icallable = Union[past_unicode, Iterable[str_or_callable]]
