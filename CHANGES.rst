

0.3
======

- Add s.unbreak(), proxy to ww.tools.strings.unbreak(), which remove lone
  line breaks.
- Add s.clean_spaces(), which applies texwrap.dedent(), unicode.strip()
  and s.unbreak()
- add s.maketrans(), similar to Python 3 unicode.maketrans() and Python 2
  string.maketrans(). But with a unified API against 2 and 3 and some
  additional shorthands.
- add s.translate(), similar to unicode.translate() but with some
  additional shorthands such as one time translation table build.
- all those new methods have a functional equivalent in ww.tools.string.
- Add s.casefold(), same as Python 3's unicode.casefold() (lower case
  for unicode), but works in python 2 as well. This means adding a
  dependency to py2casefold.
- add s.format_map() so that you have the same s() API in Python 2 and 3.
- s >> and f >> apply clean_spaces() instead of just texwrap.dedent().
- BaseWrapper.pprint() has been renamed pp().
- Generate automatic wrappers for common methods of s() so they return
  an s() object. Automatic wrappers include:

    * capitalize
    * center
    * expandtabs
    * format_map
    * ljust
    * lower
    * lstrip
    * maketrans
    * rjust
    * rstrip
    * swapcase
    * title
    * translate
    * upper
    * zfill

    This also means s() should now have full parity with unicode strings
    and a unified compatible API in Python 2 and 3.

- ww.utils now contains a backport of Python 3.5 functools.wraps(), used
  in ww.wrappers.strings.
- s.join() now proxies to ww.tools.strings.autojoin().

0.2.1
======

Just fixing the version.


0.2.0
=======


- s.replace() maxreplace is applied for the total of substitutions and not
  for separatly for each of them.
- s.replace() is type annoted and documented.
- s.replace() officially supports substitutions using a callback.
- s.replace() code has been moved to a standalone function in utils.
- g() check that all arguments are iterables and give a proper warning if not.
- way more and better documentation.
- more type definitions. Previous type definitions has been fixed.
- more checks and hints to help people debug.
- fix bug in error handling in "ww.tools.firsts()".
- coverage now generate HTML report.
- improve error handling in string concatenation.
- remove autocast on s() concatenation. Fix __radd__ on s().
- cleaning code by removing a lot TODOs, and replacing hacks by python-future.
- 100% code coverage


0.1.0
=================

- Start of the project
