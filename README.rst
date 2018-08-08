Python SyncSet
==============
When synchronizing two collections of objects, you quickly end up with code like this:

.. code-block:: python

    old_coll = get_some_items()
    new_coll = get_some_other_items()
    old_coll_map = {get_the_id(i): i for i in old_coll}
    new_coll_map = {get_the_id(i): i for i in new_coll}
    only_in_old, only_in_new, outdated, updated = [], [], [], []
    for k, old_item in old_coll_map.items():
        if k in new_coll_map:
            new_item = new_coll_map[k]
            old_changekey = get_the_changekey(old_item)
            new_changekey = get_the_changekey(new_item)
            if old_changekey > new_changekey:
                outdated.append(old_item)
                updated.append(new_item)
            elif new_changekey > old_changekey:
                outdated.append(new_item)
                updated.append(old_item)
        else:
            only_in_old.append(old_item)
    # And we still haven't built the 'only_in_new' list...

``SyncSet`` is an extension of the standard Python ``set()`` which supports this pattern with a one-liner:

.. code-block:: python

    only_in_old, only_in_new, outdated, updated = old_coll.diff(new_coll)

With ``SyncSet``, you can easily do set operations on sets of mutable and immutable objects that, in addition to the 
normal unique ID of set members, have a changekey attribute (a timestamp, autoincrement value, revision ID, hash 
etc.). Via set operations and a custom ``diff()`` method, you can do one- or two-way synchronization of comparable 
object sets via the ``OneWaySyncSet`` and ``TwoWaySyncSet`` classes, respectively. Examples are syncing files, 
web pages, contacts or calendar items.

All standard ``set()`` and ``dict()`` methods are supported, except for a handful which raise ``UndefinedBehaviorError``
because the method doesn't make sense (``>`` operator, for example). Items in the set are required to implement the very 
simple interface ``SyncSetMember``.

.. image:: https://badge.fury.io/py/syncset.svg
    :target: https://badge.fury.io/py/syncset

.. image:: https://api.codacy.com/project/badge/Grade/a35900e707cc4b71b40745d7553c26df
    :target: https://www.codacy.com/project/ecederstrand/py-syncset/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ecederstrand/py-syncset&amp;utm_campaign=Badge_Grade_Dashboard

.. image:: https://secure.travis-ci.org/ecederstrand/py-syncset.png
    :target: http://travis-ci.org/ecederstrand/py-syncset

.. image:: https://coveralls.io/repos/github/ecederstrand/py-syncset/badge.svg?branch=
    :target: https://coveralls.io/github/ecederstrand/py-syncset?branch=

Usage
~~~~~
Let's say we want to maintain a local copy of some web pages. We let the ``Last-Modified`` HTTP header decide when a page
has changed. We'll use ``date`` values in the following, for the sake of brevity.

Our URL caching code could have lots of extra functionality. Let's assume here that our main class is ``WebPage``.

First, we want to tell ``syncset`` what we consider a unique ID and a revision (changekey). We create a minimal wrapper
class that inherits ``SyncSetMember`` and makes ``url`` the unique ID and ``last_modified`` the changekey.

.. code-block:: python

    import syncset
    from datetime import date
   
   
    class WebPage:
       def __init__(self, url, last_modified):
          self.url = url
          self.last_modified = last_modified
          self.body = ''
   
       def __repr__(self):
          return self.__class__.__name__ + repr((self.url, self.last_modified))
   
   
    class SyncableWebPage(WebPage, syncset.SyncSetMember):
       def get_id(self):
          return self.url
   
       def get_changekey(self):
          return self.last_modified

We want to sync these URLs:

.. code-block:: python

    foo = "http://example.com/foo.html"
    bar = "http://example.com/bar.html"
    baz = "http://example.com/baz.html"

This is our outdated copy:

.. code-block:: python

    old_urls = syncset.OneWaySyncSet()
    old_urls.add(SyncableWebPage(foo, date(2012, 1, 1)))
    old_urls.add(SyncableWebPage(bar, date(2011, 12, 8)))


This is the server version, after fetching the latest ``Last-Modified`` header in an HTTP HEAD request:

.. code-block:: python

    new_urls = syncset.OneWaySyncSet()
    new_urls.add(SyncableWebPage(foo, date(2016, 2, 1)))
    new_urls.add(SyncableWebPage(bar, date(2011, 12, 8)))
    new_urls.add(SyncableWebPage(baz, date(2012, 2, 15)))

Now, let's find the difference between the two. ``diff()`` returns four ``SyncSet`` objects:

.. code-block:: python

    only_in_old, only_in_new, outdated_in_old, updated_in_new = old_urls.diff(new_urls)
    print(only_in_old)
    OneWaySyncSet([])
    print(only_in_new)
    
    OneWaySyncSet(
      [SyncableWebPage('http://mysrv/baz.html', datetime.date(2012, 2, 15))]
    )
    
    print(outdated_in_old)
    
    OneWaySyncSet(
      [SyncableWebPage('http://mysrv/foo.html', datetime.date(2012, 1, 1))]
    )
    
    print(updated_in_new)
    
    OneWaySyncSet(
      [SyncableWebPage('http://mysrv/foo.html', datetime.date(2012, 2, 1))]
    )

As you can see, ``foo`` needs to be updated,  ``bar`` is unchanged and ``baz`` is new on the server. After issuing HTTP
GET requests on ``foo`` and ``baz`` to get the updated content, let's update the local copy:

.. code-block:: python

    old_urls.update(new_urls)
    print(old_urls)

    OneWaySyncSet([
      SyncableWebPage('http://example.com/foo.html', datetime.date(2016, 2, 1)),
      SyncableWebPage('http://example.com/bar.html', datetime.date(2011, 12, 8)),
      SyncableWebPage('http://example.com/baz.html', datetime.date(2012, 2, 15))
    ])

This updates ``foo`` and adds ``baz``.

Similarly, a ``TwoWaySyncSet`` class exists that implements two-way synchronization. Both versions implement all the
normal ``set()`` operations, using either one-way or two-way synchronization logic.
