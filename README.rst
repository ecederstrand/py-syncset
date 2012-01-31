Python SyncSet
==============
`SyncSet` is an extension of the standard Python `set()`. With `SyncSet`, you can do set operations
on sets of objects that, in addition to the normal unique ID of set members, has a changekey
attribute (a timestamp, autoincrement value, revision ID etc.). Via set operations and a custom `diff()`
method, you can do one- or two-way synchronization of comparable object sets via the `OneWaySyncSet` and
`TwoWaySyncSet` classes, respectively. Examples are syncing files, contacts and calendar items.


Usage
~~~~~
Let's say you want so refresh a local copy of some URLs from a server. You get a timestamp from the `Last-Modified`
HTTP header.

First, we want to tell `syncset` what constitutes a unique ID is and what constitutes a revision (changekey). We 
subclass  `SyncSetMember` and make 'url' the unique ID and 'last_modified' the changekey.

>>> import syncset
>>> from datetime import datetime
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

>>> foo = "http://example.com/foo.html"
>>> bar = "http://example.com/bar.html"
>>> baz = "http://example.com/baz.html"

This is our outdated copy:

>>> myurls = syncset.OneWaySyncSet()
>>> myurls.add(SyncURL(foo, datetime(2012, 1, 1, 11, 30, 2)))
>>> myurls.add(SyncURL(bar, datetime(2011, 8, 1, 17, 23, 2)))
>>> myurls.add(SyncURL(baz, datetime(2012, 2, 1, 9, 12, 3)))


This is the server version. You could get the `Last-Modified` header in an HTTP HEAD request:

>>> serverurls = syncset.OneWaySyncSet()
>>> serverurls.add(SyncURL(foo, datetime(2012, 2, 1, 9, 12, 23)))
>>> serverurls.add(SyncURL(bar, datetime(2011, 12, 8, 2, 6, 18)))
>>> serverurls.add(SyncURL(baz, datetime(2012, 2, 1, 9, 12, 3)))

Now, show us the difference between the two. `diff()` returns four `SyncSet` (only_in_self, only_in_master, outdated_in_self, updated_in_master):

>>> myurls.diff(serverurls)
(OneWaySyncSet([]), OneWaySyncSet([]), OneWaySyncSet([SyncURL('http://example.com/foo.html', datetime.datetime(2012, 1, 1, 11, 30, 2)), SyncURL('http://example.com/bar.html', datetime.datetime(2011, 8, 1, 17, 23, 2))]), OneWaySyncSet([SyncURL('http://example.com/foo.html', datetime.datetime(2012, 2, 1, 9, 12, 23)), SyncURL('http://example.com/bar.html', datetime.datetime(2011, 12, 8, 2, 6, 18))]))

As you can see, `foo` and `bar` needs to be updated, while `baz` is unchanged. Now we do whatever is needed to fetch the new data in our program. Then, let's update the local copy:

>>> myurls.update(serverurls)
OneWaySyncSet([SyncURL('http://example.com/foo.html', datetime.datetime(2012, 2, 1, 9, 12, 23)), SyncURL('http://example.com/bar.html', datetime.datetime(2011, 12, 8, 2, 6, 18)), SyncURL('http://example.com/baz.html', datetime.datetime(2012, 2, 1, 9, 12, 3))])


Similarly, a `TwoWaySyncSet` class exists that implements two-way synchronization. Boths versions implement all the normal `set()` operations, using either one-way or two-way sync semantics.