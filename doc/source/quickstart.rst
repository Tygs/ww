What can I do with WW?
======================

First of all, there is absolutely nothing you can do with WW that you can’t do with simple Python.

In fact, WW simply provides you a set of convenient tools to ease the usage of Python primitives
and better exploit the wonders of the standard library.

So, what you *can* do is basically use those wrappers like you would do with primitive types,
and use advanced functions like they always were part of those objects.

Let’s take a simple example. Like every Python programmer, you like lists. Lists are awesome.
And adding things to lists is the most natural thing in the world. That’s so natural that no one
could blame you for adding multiple things to a list.

.. code-block:: python

    >>> lst = [1, 2]
    >>> lst.append(3)
    >>> lst.append(4)

If you’re new to Python, you may have tried something like this instead:

.. code-block:: python

    >>> lst = [1, 2]
    >>> lst.append(3, 4).append(5)

Because that would have made perfect sense. And, because of Python is about thinks that make
sense, WW gives you this logical syntax. All that you have to do is explicitely tell that you’re
using WW wrapper.

.. code-block:: python

    >>> from ww import l
    >>> lst = l([1, 2]) # wrap your list in the wonderful wrapper
    >>> lst.append(3, 4).append(5)
    [1, 2, 3, 4, 5]

`lst` is an instance of `<ww.wrappers.lists.ListWrapper>`, that we just imported as the simple
name `l` (we’ll use the short name from now). A `l` object is just a regular Python list, with
some bonuses, like this chaining `append()` method.

From the time you’ll start to use `l` objects, any method or operator on those objects will start
to return other `l` objects, so you don’t have to wrap them explicitely.

WW has many wrappers:

- l for lists
- t for tuples
- g for iterables
- d for dictionaries
- s for strings

They all come with transparent compatibility with builtin Python types, and add cool features.

Right now you'll find some features are missing or undocumented, since we are still in version 0.1. But it's progressing steadily.
