Wonderful Wrappers
====================

.. image:: http://travis-ci.org/Tygs/ww.svg?branch=master
    :target: https://travis-ci.org/Tygs/ww
.. image:: http://coveralls.io/repos/github/Tygs/ww/badge.svg?branch=master
    :target: https://coveralls.io/github/Tygs/ww?branch=master

Developement
-------------

Install for dev::

    python setup.py develop

Style Guide :
 - Python: `PEP8`_
 - Docstrings: `Google style`_

Deactivate dev mode:

    python setup.py develop --uninstall

Running all tests::

    python setup.py test

After that, you can run tests covergage this way::

    # cmd only coverage
    py.test --cov ww tests
    # dump an HTML report in htmlcov dir
    py.test  --cov-report html --cov ww tests


.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _Google style: http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
