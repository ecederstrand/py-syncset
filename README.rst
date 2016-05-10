Python SyncSet
==============
``SyncSet`` is an extension of the standard Python ``set()``. With ``SyncSet``, you can do set operations
on sets of mutable and immutable objects that, in addition to the normal unique ID of set members, has a changekey
attribute (a timestamp, autoincrement value, revision ID, hash etc.). Via set operations and a custom ``diff()``
method, you can do one- or two-way synchronization of comparable object sets via the ``OneWaySyncSet`` and
``TwoWaySyncSet`` classes, respectively. Examples are syncing files, contacts and calendar items.

All standard ``set()`` and ``dict()`` methods are supported, except for a handful which raise ``UndefinedBehaviorError``
because the method doesn't make sense (``>`` operator, for example).


Usage
~~~~~
Let's say we want to maintain a local copy of some web pages. We let the ``Last-Modified``HTTP header decide when a page
has changed. We'll use ``date`` values in the following, for the sake of brevity.

Our URL caching code could have lots of extra functionality. Let's assume here that out main class is ``WebPage``.

First, we want to tell ``syncset`` what we consider a unique ID and a revision (changekey). We create a minimal wrapper
class that inherits ``SyncSetMember`` and makes ``url`` the unique ID and ``last_modified`` the changekey.

>>> import syncset
>>> from datetime import date
>>>
>>>
>>> class WebPage:
>>>    def __init__(self, url, last_modified):
>>>       self.url = url
>>>       self.last_modified = last_modified
>>>       self.body = ''
>>>
>>>    def __repr__(self):
>>>       return self.__class__.__name__ + repr((self.url, self.last_modified))
>>>
>>>
>>> class SyncableWebPage(WebPage, syncset.SyncSetMember):
>>>    def get_id(self):
>>>       return self.url
>>>
>>>    def get_changekey(self):
>>>       return self.last_modified

We want to sync these URLs:

>>> foo = "http://example.com/foo.html"
>>> bar = "http://example.com/bar.html"
>>> baz = "http://example.com/baz.html"

This is our outdated copy:

>>> old_urls = syncset.OneWaySyncSet()
>>> old_urls.add(SyncableWebPage(foo, date(2012, 1, 1)))
>>> old_urls.add(SyncableWebPage(bar, date(2011, 12, 8)))


This is the server version, after fetching the latest ``Last-Modified`` header in an HTTP HEAD request:

>>> new_urls = syncset.OneWaySyncSet()
>>> new_urls.add(SyncableWebPage(foo, date(2016, 2, 1)))
>>> new_urls.add(SyncableWebPage(bar, date(2011, 12, 8)))
>>> new_urls.add(SyncableWebPage(baz, date(2012, 2, 15)))

Now, let's find the difference between the two. ``diff()`` returns four ``SyncSet`` objects:

>>> only_in_old, only_in_new, outdated_in_old, updated_in_new = old_urls.diff(new_urls)
>>> only_in_old
OneWaySyncSet([])
>>> only_in_new
OneWaySyncSet([SyncableWebPage('http://mysrv/baz.html', datetime.date(2012, 2, 15))])
>>> outdated_in_old
neWaySyncSet([SyncableWebPage('http://mysrv/foo.html', datetime.date(2012, 1, 1))])
>>> updated_in_new
OneWaySyncSet([SyncableWebPage('http://mysrv/foo.html', datetime.date(2012, 2, 1))])

As you can see, ``foo`` needs to be updated,  ``bar`` is unchanged and ``baz`` is new on the server. After issuing HTTP
GET requests on ``foo`` and ``baz`` to get the updated content, let's update the local copy:

>>> old_urls.update(new_urls)
>>> old_urls
... OneWaySyncSet([
...   SyncableWebPage('http://example.com/foo.html', datetime.date(2016, 2, 1)),
...   SyncableWebPage('http://example.com/bar.html', datetime.date(2011, 12, 8)),
...   SyncableWebPage('http://example.com/baz.html', datetime.date(2012, 2, 15))
... ])

This updates ``foo`` and adds ``baz``.

Similarly, a ``TwoWaySyncSet`` class exists that implements two-way synchronization. Both versions implement all the
normal ``set()`` operations, using either one-way or two-way synchronization logic.
