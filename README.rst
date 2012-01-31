Python SyncSet
==============
``SyncSet`` is an extension of the standard Python ``set()``. With ``SyncSet``, you can do set operations
on sets of objects that, in addition to the normal unique ID of set members, has a changekey
attribute (a timestamp, autoincrement value, revision ID etc.). Via set operations and a custom ``diff()``
method, you can do one- or two-way synchronization of comparable object sets via the ``OneWaySyncSet`` and
``TwoWaySyncSet`` classes, respectively. Examples are syncing files, contacts and calendar items.


Usage
~~~~~
Let's say you want so refresh a local copy of some URLs from a server. You get a timestamp from the ``Last-Modified``
HTTP header. I'm using ``date`` for sake of brevity.

First, we want to tell ``syncset`` what constitutes a unique ID is and what constitutes a revision (changekey). We 
subclass  ``SyncSetMember`` and make ``url`` the unique ID and ``last_modified`` the changekey.

>>> import syncset
>>> from datetime import date
>>>
>>> class SyncURL(syncset.SyncSetMember):
>>>   def __init__(self, url, last_modified):
>>>      self.url = url
>>>      self.last_modified = last_modified
>>>
>>>   def get_id(self): return self.url
>>>   def get_changekey(self): return self.last_modified
>>>   def __repr__(self): return self.__class__.__name__+repr((self.url, self.last_modified))

We want to sync these URLs:

>>> foo = "http://mysrv/foo.html"
>>> bar = "http://mysrv/bar.html"
>>> baz = "http://mysrv/baz.html"

This is our outdated copy:

>>> myurls = syncset.OneWaySyncSet()
>>> myurls.add(SyncURL(foo, date(2012, 1, 1)))
>>> myurls.add(SyncURL(bar, date(2011, 12, 8)))


This is the server version. You could get the ``Last-Modified`` header in an HTTP HEAD request:

>>> serverurls = syncset.OneWaySyncSet()
>>> serverurls.add(SyncURL(foo, date(2012, 2, 1)))
>>> serverurls.add(SyncURL(bar, date(2011, 12, 8)))
>>> serverurls.add(SyncURL(baz, date(2012, 2, 15)))

Now, show us the difference between the two. ``diff()`` returns four ``SyncSet`` (only_in_self, only_in_master, outdated_in_self, updated_in_master):

>>> only_in_self, only_in_master, outdated_in_self, updated_in_master = myurls.diff(serverurls)
>>> only_in_self
OneWaySyncSet([])
>>> only_in_master
OneWaySyncSet([SyncURL('http://mysrv/baz.html', datetime.date(2012, 2, 15))])
>>> outdated_in_self
neWaySyncSet([SyncURL('http://mysrv/foo.html', datetime.date(2012, 1, 1))])
>>> updated_in_master
OneWaySyncSet([SyncURL('http://mysrv/foo.html', datetime.date(2012, 2, 1))])

As you can see, ``foo`` needs to be updated,  ``bar`` is unchanged and ``baz`` is new on the server. [Now we do whatever
is needed to fetch the new and updated data in our program]. Let's update the local copy:

>>> myurls.update(serverurls)
OneWaySyncSet([SyncURL('http://mysrv/foo.html', datetime.date(2012, 2, 1)), SyncURL('http://mysrv/bar.html', \
...   datetime.date(2011, 12, 8)), SyncURL('http://mysrv/baz.html', datetime.date(2012, 2, 15))])

This updates ``foo`` and adds ``baz``.

Similarly, a ``TwoWaySyncSet`` class exists that implements two-way synchronization. Boths versions implement all the normal ``set()`` operations, using either one-way or two-way sync semantics.