Wonderful Wrappers
====================

.. image:: http://travis-ci.org/Tygs/ww.svg?branch=master
    :target: https://travis-ci.org/Tygs/ww
.. image:: http://coveralls.io/repos/github/Tygs/ww/badge.svg?branch=master
    :target: https://coveralls.io/github/Tygs/ww?branch=master
.. image:: https://readthedocs.org/projects/wonderful-wrappers/badge/?version=latest
    :target: http://wonderful-wrappers.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Unobtrusive wrappers improving Python builtins and more.

Ever wish you could...
------------------------

lazily slice generators?

::

    >>> from ww import g
    >>> gen = g(x * x for x in range(100))
    >>> gen
    <IterableWrapper generator>
    >>> for element in g(x * x for x in range(100))[3: 6]:
    ...     print(element)
    ...
    9
    16
    25

add dictionaries?

::

    >>> from ww import d
    >>> dic = d({'a': 1})
    >>> dic
    {'a': 1}
    >>>  dic + {'b': 2}
    {'b': 2, 'a': 1}

have a `len` attribute on lists?

::

    >>> from ww import l
    >>> lst = l([1, 2, 3])
    >>> lst
    [1, 2, 3]
    >>> lst.len
    3

`join()` from tuple?

::

    >>> from ww import t
    >>> tpl = t((1, 2, 3))
    >>> tpl
    (1, 2, 3)
    >>> tpl.join(',')  # oh, it also autocasts to string. And its configurable.
    u'1,2,3'

`replace()` multiple caracters at once in a string?

::

    >>> from ww import s
    >>> string = s('fizz buzz')
    >>> string  # strings try very hard to be consistent on Python 2 and 3
    u'fizz buzz'
    >>> string.replace(('i', 'u'), 'o')  # the original signature is ok too
    u'fozz bozz'

And there are many, many, more goodies.

Install them with::

    pip install ww

Then `read the doc`_.

Versions infos
---------------

**Compatibility:** CPython 2.7+/3.3+ and the last stable versions of pypy2/3.
**Platform:** It should be any as the lib is pure Python and is not OS related.
But right now we only tested it on GNU/Linux.
**Version:** 0.1

WARNING
--------

The software is currently in early stage. Only s() and g() are considered
well documented and tested, and even them deserve some more love.
You'll also meet some empty files for future ideas.

We choose to make an early release under the pressing request of colleagues
eager to try it but it's not the final product. Quality is on the way.

Also, we WILL break the API until we reach 1.0, from which we'll switch
to semver and secure the API.


Development
------------

You can offer PR with your contributions to ww. They should include unit tests,
docstrings, type definitions and a new entry in the documentation.

Install for dev::

    python setup.py develop
    pip install -r dev-requirements.txt

Style Guide :
 - Python: `PEP8`_
 - Docstrings: `Google style`_

Deactivate dev mode:

    python setup.py develop --uninstall

Running all tests on your current Python::

    python setup.py test

Run tests coverage with your current Python::

    # cmd only coverage
    py.test --cov ww tests
    # dump an HTML report in htmlcov dir
    py.test  --cov-report html --cov ww tests

Running all the tests with all Python versions,
build the doc, scan the code with flake8 and mypy and recalculate coverage::

    tox

Before you do a PR, it's better if you can do this. If you can't
(e.g: you can't install one of the Python targets), please let us know in the
PR comments.

.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _Google style: http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
.. _Read the doc: http://wonderful-wrappers.readthedocs.io/
