



0.1.1
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
