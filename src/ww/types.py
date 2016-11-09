

from past.builtins import unicode as past_unicode

try:
    unicode = unicode  # type: ignore
except NameError:
    unicode = str

# Hack to be able to use typing.TYPE_CHECKING even when typing is not installed
# such as in Python 2
try:
    import typing
except ImportError:  # pragma: no cover
    class _:  # pylint: disable=too-few-public-methods
        TYPE_CHECKING = False
    locals()['typing'] = _

try:
    from typing import Union, Iterable, Callable, Any, TypeVar, Hashable
    T = TypeVar('T')
    T2 = TypeVar('T2')
    C = TypeVar('C', bound=Callable)
    I = TypeVar('I', bound=Iterable)
    istr = Iterable[past_unicode]
    str_istr = Union[past_unicode, istr]
    str_or_callable = Union[past_unicode, Callable]
    str_istr_icallable = Union[past_unicode, Iterable[str_or_callable]]
except ImportError:  # pragma: no cover
    # Declare types anyway so we can import them even when typing is not
    # installed
    if not typing.TYPE_CHECKING:
        Union = None
        Iterable = None
        Any = None
        Callable = None
        str_istr = None
        str_istr_icallable = None
        TypeVar = None
        T = None
        C = None
        I = None
        T2 = None
        Hashable = None
