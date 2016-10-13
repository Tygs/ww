Wonderful Wrappers
====================

Developement
-------------

Install for dev::

    python setup.py develop

Style Guide :
 - Python: PEP8 (https://www.python.org/dev/peps/pep-0008/)
 - JS: Google (http://google-styleguide.googlecode.com/svn/trunk/javascriptguide.xml)

Deactivate dev mode:

    python setup.py develop --uninstall

Running all tests::

    python setup.py test

After that, you can run tests covergage this way::

    # cmd only coverage
    py.test --cov ww tests
    # dump an HTML report in htmlcov dir
    py.test  --cov-report html --cov ww tests
