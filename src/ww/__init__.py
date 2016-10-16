

__version__ = "0.1.0"

from .wrappers.iterables import IterableWrapper as g  # noqa
from .wrappers.strings import StringWrapper as s, FStringWrapper as f  # noqa
from .wrappers.lists import ListWrapper as l  # noqa
from .wrappers.tuples import TupleWrapper as t  # noqa
from .wrappers.dicts import DictWrapper as d  # noqa

# TODO: wrapper for datetime
# TODO: wrapper for path.py
l
