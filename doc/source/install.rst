Installation
============

Dependencies
------------

Wonderful Wrappers (WW) obviously need a working Python installation, since it is designed to work with it.
Any Python version installed at the time of reading should be compatible: Cpython from 2.7 to 3.5, Pypy 2 and 3…

In order to work nicely with both major Python versions, some compatibility external packages are needed,
and will be automatically installed with the standard install procedure. For your information, those are the
required external modules:

- future
- six

Additionnally, some other external packages are useful for WW, but not required: you can exploit most of
the features of WW without them. Don’t worry, you’ll get clear error messages if you try to use a
feature that need an optional dependency.

- chardet
- formatizer

Now for the fun part. Installing WW is as easy as this, typed in a console:

.. code-block:: shell

    pip install ww

On a POSIX system (like GNU/Linux or UNIX), you may want to make this installation available only for
the current user (and avoid system-wide install).

.. code-block:: shell

    pip install --user ww

This will install the lightest set of features for WW, pulling the minimum dependencies. That would be
useful for inclusion in a production-ready project, but you may prefer the full set of features while
you play around with it (obviously, the `--user` option is still valid).

.. code-block:: shell

    pip install ww[all]

There is more: you may want to accept some additional dependencies in your project, but not **that one**,
that comes with the full set of WW. You can specify the exact features you want to be available with your
WW installation. For example, this will install only the `chardet` dependency, after the required ones.

.. code-block:: shell

    pip install ww[chardet]

The full list of options is here:

- `chardet` (for automatic charset detections in strings conversions)
- `formatizer` (for F-strings)

Alternatively, you can install WW from source. This enables to install the latest, fresh-baked, version
from Github instead of PyPI. To do so, you first have to fetch the WW source (download the archive, *git-clone* it…),
then type in a terminal, within the directory containing the sources:

.. code-block:: shell

    pip install .
