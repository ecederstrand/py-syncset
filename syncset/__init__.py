import logging


class UndefinedBehaviorError(ArithmeticError):
    pass


class SyncSet(set):
    """
    An extension of ``set()`` which, in addition to the usual membership
    operators, also supports comparing syncset members that are logically
    the same but have different object revisions. Operations are
    based on the object id and changekey (aka. revision, timestamp etc.).

    Don't use this class directly. Use the ``OneWay`SyncSet`` or ``TwoWaySyncSet`` 
    implementation instead to choose between "master wins" and 
    "newest-version-wins" semantics.

    Set members can extend ``SyncSetMember`` which defines the requirements
    for syncset members.

    To be able to get a syncset member by id, ```SyncSet`` also implements 
    parts of the ``dict()`` interface, so retrieval by id is cheap compared to 
    a ``set()``.

    The ``isdisjoint``, ``issubset`` and ``issuperset`` methods return 
    ``UndefinedBehaviorError`` instead of implicitly using the base ``set()`` 
    implementation because it is not defined what the return values are in the 
    context of syncset members with changekeys. Use the ``diff()`` method of 
    ``OneWaySyncSet`` and ``TwoWaySyncSet`` instead.
    """
    def __init__(self, iterable=None):
        if not iterable: iterable = []
        self.logger = logging.getLogger('%s.%s' %
                        (__name__, self.__class__.__name__))

        super(SyncSet, self).__init__()
        self.item_dict = dict()
        # Make sure items enter the syncset the way we want by ising the add() method.
        [self.add(item) for item in iterable]

    def copy(self):
        """
        Return a copy of self
        """
        obj = super(SyncSet, self).copy()
        obj.item_dict = self.item_dict.copy()
        return obj

    def sync(self, deleted, updated, new):
        """
        Update syncset with changes in-place
        """
        self.difference_update(deleted)
        self.symmetric_difference_update(updated)
        self.add(new)

    def add(self, item):
        raise NotImplementedError()

    def __contains__(self, item):
        """
        Only returns ``True`` if the same version of the item is present
        """
        if item.get_id() in self.item_dict:
            return self.item_dict[item.get_id()].__cmp__(item) == 0
        return False

    def contains_similar(self, item):
        """
        Returns true if an object with the same id exists is present
        """
        return item.get_id() in self.item_dict

    def __getitem__(self, item_id):
        """
        Gets an object by id using syncset[item_id]
        """
        return self.item_dict[item_id]

    def get(self, item_id, default=None):
        return self[item_id] if item_id in self.item_dict else default

    def __ior__(self, *others):
        """
        The |= operator. Alias for ``update()``
        """
        return self.update(*others)

    def update(self, *others):
        """
        Update the set, adding elements from all others
        """
        for other in others:
            [self.add(item) for item in other]
        return self

    def __iand__( self, *others):
        """
        The ``&=`` operator. Alias for ``intersection_update``
        """
        return self.intersection_update(*others)

    def intersection_update(self, *others):
        """
        Update the set, keeping only elements found in it and all ``others``.
        """
        for other in others:
            [self.remove(item) for item in (self.difference(other))]
            [self.add(item) for item in (self.intersection(other))]
        return self

    def __isub__(self, *others):
        """
        The ``-=`` operator. Alias for ``difference_update``
        """
        return self.difference_update(*others)

    def difference_update(self, *others):
        """
        Update the syncset, removing elements found in ``others``.
        """
        for other in others:
            [self.discard(item) for item in other]
        return self

    def __ixor__(self, other):
        """
        The ``^=`` operator. Alias for ``intersection_update``
        """
        return self.symmetric_difference_update(other)

    def symmetric_difference_update(self, other):
        """
        Update the syncset, keeping only elements found in either set, but not in both.
        """
        to_remove = self.intersection(other)
        to_add = other.difference(self)
        [self.remove(item) for item in to_remove]
        [self.add(item) for item in to_add]
        return self

    def remove(self, item):
        del self.item_dict[item.get_id()]
        super(SyncSet, self).remove(item)

    def discard(self, item):
        if item.get_id() in self.item_dict:
            self.remove(item)

    def pop(self):
        get_id, item = self.item_dict.popitem()
        super(SyncSet, self).remove(item)
        return item

    def clear(self):
        self.item_dict.clear()
        super(SyncSet, self).clear()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if len(self) != len(other): return False
        for item in self:
            if not item in other:
                return False
        return True

    def isdisjoint(self, other):
        raise UndefinedBehaviorError('The result of this operator is undefined')

    def __le__(self, other):
        return self.issubset(other)

    def issubset(self, other):
        raise UndefinedBehaviorError('The result of this operator is undefined')

    def __lt__(self, other):
        raise UndefinedBehaviorError('The result of this operator is undefined')

    def __ge__(self, other):
        return self.issuperset(other)

    def issuperset(self, other):
        raise UndefinedBehaviorError('The result of this operator is undefined')

    def __gt__(self, other):
        raise UndefinedBehaviorError('The result of this operator is undefined')

    def __or__(self, *others):
        return self.union(self, *others)

    def union(self, *others):
        """
        Return a new syncset with elements from the syncset and all others
        """
        items = self.copy()
        for other in others:
            [items.add(item) for item in other]
        return items

    def __and__(self, *others):
        return self.intersection(self, *others)

    def __sub__(self, *others):
        return self.difference(self, *others)

    def difference(self, *others):
        """
        Return a new syncset with elements in the syncset that are not in the others
        """
        items = self.copy()
        for other in others:
            [items.discard(item) for item in other]
        return items

    def __xor__(self, other):
        return self.symmetric_difference(self, other)

    def symmetric_difference(self, other):
        """
        Return a new syncset with elements in either the syncset or other but not both
        """
        return self.__class__(super(SyncSet, self).symmetric_difference(other))


class OneWaySyncSet(SyncSet):
    """
    Implements one way diff with a master ``SyncSet``. Diffing is based
    on an id and changekey of syncset members.

    Set members can extend ``SyncSetMember`` which defines the requirements
    for syncset members. One way diff only needs changekey values to be comparable, 
    not sortable.
    
    For all methods defined in this class, data passed in arguments are preferred
    to existing data.
    """
    def diff(self, master):
        """
        Returns four SyncSets containing the members that are only in self,
        only in other, outdated in self, updated in master.
        """
        only_in_self = self.difference(master)
        only_in_master = master.difference(self)
        common = self.intersection(master)
        updated_in_master = self.__class__()
        outdated_in_self = self.__class__()
        for item in common:
            common_id = item.get_id()
            self_item = self[common_id]
            master_item = master[common_id]
            # force __cmp__(); cmp(a, b) somehow prefers a.__eq__
            if self_item.__cmp__(master_item) != 0:
                self.logger.debug('oneway diff: %s differs from %s' % (self_item, master_item))
                updated_in_master.add(master_item)
                outdated_in_self.add(self_item)
        return only_in_self, only_in_master, outdated_in_self, updated_in_master

    def add(self, item):
        self.discard(item)
        self.item_dict[item.get_id()] = item
        super(SyncSet, self).add(item)

    def intersection(self, *others):
        """
        Return a new syncset with elements common to the syncset and all others. For 
        common elements, the last one among the sets are preferred.
        """
        items = self.__class__()
        for item in self:
            item_id = item.get_id()
            try:
                common_item = [other[item_id] for other in others][-1]
                items.add(common_item)
            except KeyError:
                pass
        return items


class TwoWaySyncSet(SyncSet):
    """
    Implements two way diff with a ``SyncSet``. Diffing is based
    on an id and changekey of syncset members.

    Set members can extend ``SyncSetMember`` which defines the interface for 
    syncset members. Two way diff needs changekey values to be sortable (e.g. 
    a revision number or a timestamp).

    For all methods defined in this class, data passed in arguments are 
    preferred to existing data only if existing data is older.
    """
    def diff(self, other):
        """
        Returns four SyncSets containing the members that are only in self, only
        in other, newer in self, and newer in other.
        """
        only_in_self = self.difference(other)
        only_in_other = other.difference(self)
        common = self.intersection(other)
        newer_in_self = self.__class__()
        newer_in_other = self.__class__()
        for item in common:
            common_id = item.get_id()
            self_item = self[common_id]
            other_item = other[common_id]
            if self_item > other_item:
                self.logger.debug('diff: %s larger than %s' % (self_item, other_item))
                newer_in_self.add(self_item)
            elif self_item < other_item:
                self.logger.debug('diff: %s smaller than %s' % (self_item, other_item))
                newer_in_other.add(other_item)
        return only_in_self, only_in_other, newer_in_self, newer_in_other

    def add(self, item):
        """
        Add a new item. Only replace an existing item if the existing item is older
        """
        existing_item = self.item_dict.get(item.get_id())
        if existing_item:
            if existing_item >= item:
                return
            else:
                self.remove(item)
        self.item_dict[item.get_id()] = item
        super(SyncSet, self).add(item)

    def intersection(self, *others):
        """
        Return a new syncset with elements common to the syncset and all others. 
        For common elements, the newest one among the sets are preferred.
        """
        items = self.__class__()
        for item in self:
            item_id = item.get_id()
            try:
                common_item = max([other[item_id] for other in others])
                items.add(common_item)
            except KeyError:
                pass
        return items


class SyncSetMember(object):
    """
    Defines the requirements of members of a ``SyncSet``. Meant to be subclassed
    by consumers. Override at least ``get_id``and ``get_changekey`` methods when
    subclassing.

    The value returned by get_id must be hashable and must never change through 
    the lifetime of the object.

    When used for one way syncing, changekeys must only be comparable. When used 
    for two way syncing, changekey values must be logically sortable using 
    cmp(a, b).
    """
    def get_id(self):
        """
        Return whatever the object regards as a unique id. Must return
        a hashable object.
        """
        raise NotImplementedError()

    def get_changekey(self):
        """
        Return whatever the object regards as an object version or revision.
        Must return a comparable object (implements __cmp__). For two-way syncing,
        must return a sortable object.
        """
        raise NotImplementedError()

    def __hash__(self):
        """
        Needed to ensure that only one version of an object exists in the syncset
        """
        return hash(self.get_id())

    def __eq__(self, other):
        """
        Compare members by id only
        """
        return hash(self) == hash(other)

    def __cmp__(self, other):
        """
        Compares members by id and changekey
        """
        c = cmp(self.get_id(), other.get_id())
        if c != 0: return c
        # Use the comparison implementation of whatever object type
        # is used as changekey.
        return cmp(self.get_changekey(), other.get_changekey())


class DemoMember(SyncSetMember):
    """
    Provided as an example of subclassing SyncSetMember. Models a simple VCS.
    """
    def __init__(self, filename, revision):
        self.filename = filename
        self.revision = revision

    def get_id(self):
        return self.filename

    def get_changekey(self):
        return self.revision

    def __repr__(self):
        return self.__class__.__name__+repr((self.filename, self.revision))

    def __unicode__(self):
        return u'File: %s revision: %s' % (self.filename, self.revision)