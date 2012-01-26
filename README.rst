Python SyncSet
==============
SyncSet is an extension of the standard Python set(). With SyncSet, you can do set operations
on sets of objects that, in addition to the normal unique ID of set() members, has a revision
attribute (a timestamp, autoincrement value, revision ID etc.). With the set operations, you
can do one- or two-way synchronization of comparable object sets. Examples are syncing files,
contacts and calendar items.


Usage
~~~~~
