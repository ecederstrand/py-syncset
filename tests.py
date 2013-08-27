# -*- coding: utf-8 -*-

import unittest
from datetime import datetime
from syncset import SyncSet, OneWaySyncSet, TwoWaySyncSet, SyncSetMember, UndefinedBehaviorError


# Create a minimal implementation of the SyncSetMember interface
class TestMember(SyncSetMember):
    def __init__(self, uid, changekey):
        self.uid = uid
        self.changekey = changekey

    def get_id(self): return self.uid
    def get_changekey(self): return self.changekey
    def __repr__(self): return self.__class__.__name__+repr((self.uid, self.changekey))
    def __unicode__(self): return repr(self)
    def __str__(self): return unicode(self)


class _OneWayBaseClass(unittest.TestCase):

    def setUp(self):
        self.myslave = OneWaySyncSet()
        self.mymaster = OneWaySyncSet()
        self.a1 = TestMember('a', 1)
        self.a2 = TestMember('a', 2)
        self.a3 = TestMember('a', 3)
        self.b1 = TestMember('b', 1)
        self.b2 = TestMember('b', 2)
        self.b3 = TestMember('b', 3)
        self.c1 = TestMember('c', 1)
        self.c2 = TestMember('c', 2)
        self.c3 = TestMember('c', 3)


class _TwoWayBaseClass(unittest.TestCase):

    def setUp(self):
        self.myset = TwoWaySyncSet()
        self.otherset = TwoWaySyncSet()
        self.a1 = TestMember('a', 1)
        self.a2 = TestMember('a', 2)
        self.a3 = TestMember('a', 3)
        self.b1 = TestMember('b', 1)
        self.b2 = TestMember('b', 2)
        self.b3 = TestMember('b', 3)
        self.c1 = TestMember('c', 1)
        self.c2 = TestMember('c', 2)
        self.c3 = TestMember('c', 3)


class SyncSetMemberTest(unittest.TestCase):
    def _test_member(self, low, high):
        a1 = TestMember(low, low)
        a2 = TestMember(low, high)
        b1 = TestMember(high, low)
        b2 = TestMember(high, high)

        self.assertTrue(a1.__eq__(a1))
        self.assertTrue(a1.__eq__(a2))
        self.assertFalse(a1.__eq__(b1))
        self.assertEqual(a1.__cmp__(a1), 0)
        self.assertLess(a1.__cmp__(a2), 0)
        self.assertGreater(a2.__cmp__(a1), 0)
        self.assertLess(a1.__cmp__(b1), 0)
        self.assertGreater(b1.__cmp__(a1), 0)
        self.assertGreater(b2.__cmp__(a1), 0)

        self.assertEqual(TestMember(low, low), TestMember(low, low))
        self.assertEqual(TestMember(low, low), TestMember(low, high))
        self.assertEqual(TestMember(low, high), TestMember(low, low))
        self.assertNotEqual(TestMember(low, low), TestMember(high, low))
        self.assertNotEqual(TestMember(high, low), TestMember(low, low))
        self.assertGreater(TestMember(low, high), TestMember(low, low))
        self.assertLess(TestMember(low, low), TestMember(low, high))

    def test_member(self):
        m = TestMember(1, 2)
        self.assertEqual(m.get_id(), 1)
        self.assertEqual(m.get_changekey(), 2)
        self.assertRaises(TypeError, hash, TestMember([1, 'a'], [1, 'b']))

    def test_member_compare(self):
        """Test SyncSetMember implementation for different object types"""
        # Integers
        self._test_member(1, 2)
        # Floats
        self._test_member(1.0, 1.1)
        # Strings
        self._test_member('alpha', 'beta')
        # Unicode
        self._test_member(u'æble', u'øvelse')
        # Tuples
        self._test_member(('a', 'b'), ('a', 'c'))
        # Datetimes
        self._test_member(datetime(2010, 1, 1, 8, 0, 0), datetime(2010, 1, 1, 10, 0, 0))
        # All other id and changekey types must implement __hash__, __eq__ and __cmp__
        # according to SyncSetMember specs.


class OneWaySyncSetTest(_OneWayBaseClass):
    def test_constructor(self):
        self.assertEqual(self.myslave, self.mymaster)
        self.assertEqual(self.myslave.item_dict, self.mymaster.item_dict)
        self.myslave = OneWaySyncSet([self.a1, self.b1, self.c1])
        self.mymaster = OneWaySyncSet([self.a1, self.b1, self.c1])
        self.assertEqual(self.myslave, self.mymaster)
        self.assertEqual(self.myslave.item_dict, self.mymaster.item_dict)
        self.mymaster = OneWaySyncSet([self.c1, self.a1, self.b1])
        self.assertEqual(self.myslave, self.mymaster)
        self.assertEqual(self.myslave.item_dict, self.mymaster.item_dict)
        self.assertEqual(OneWaySyncSet([self.a2, self.a1]), OneWaySyncSet([self.a3, self.a1]))
        self.assertNotEqual(OneWaySyncSet([self.a2, self.a1]), OneWaySyncSet([self.a1, self.a2]))
        self.assertFalse(OneWaySyncSet([self.a2, self.a1]) == OneWaySyncSet([self.a1, self.a2]))
        self.assertNotEqual(OneWaySyncSet([self.a1, self.b1]), OneWaySyncSet([self.a1, self.b2]))
        self.assertFalse(OneWaySyncSet([self.a1, self.b1]) == OneWaySyncSet([self.a1, self.b2]))

    # Basic methods
    def test_copy(self):
        self.myslave = OneWaySyncSet([self.a1])
        slave_copy = self.myslave.copy()
        self.assertIsInstance(slave_copy, OneWaySyncSet)

    def test_add(self):
        for m in (self.a1, self.b1, self.c1):
            self.myslave.add(m)
        self.assertEqual(len(self.myslave), 3)
        self.assertEqual(self.myslave[self.a1.get_id()], self.a1)
        self.assertNotEqual(self.myslave[self.a1.get_id()], self.b1)
        self.assertNotEqual(self.myslave[self.a1.get_id()], self.c1)
        self.assertEqual(self.myslave[self.b1.get_id()], self.b1)
        self.assertEqual(self.myslave[self.c1.get_id()], self.c1)

    def test_versions_add(self):
        # Also tests __getitem__
        for m in (self.a2, self.a1):
            self.myslave.add(m)
        self.assertEqual(len(self.myslave), 1)
        self.assertTrue(self.myslave[self.a2.get_id()].__eq__(self.a1))
        self.assertEqual(self.myslave[self.a2.get_id()].__cmp__(self.a1), 0)
        self.assertNotEqual(self.myslave[self.a2.get_id()].__cmp__(self.a2), 0)

    def test_clear(self):
        for m in (self.a1, self.b3):
            self.myslave.add(m)
        self.myslave.clear()
        self.assertTrue(len(self.myslave) == 0)

    def test_len(self):
        for m in (self.a1, self.a2):
            self.myslave.add(m)
        self.assertTrue(len(self.myslave) == 1)
        self.myslave.add(self.b1)
        self.assertTrue(len(self.myslave) == 2)

    # Basic operators
    def test_contains(self):
        self.myslave.add(self.a1)
        self.assertIn(self.a1, self.myslave)
        self.assertNotIn(self.a2, self.myslave)
        self.assertNotIn(self.a3, self.myslave)

    def test_contains_similar(self):
        self.myslave.add(self.a1)
        self.assertTrue(self.myslave.contains_similar(self.a1))
        self.assertTrue(self.myslave.contains_similar(self.a2))
        self.assertFalse(self.myslave.contains_similar(self.b1))

    def test_equal(self):
        self.assertEqual(OneWaySyncSet([self.a1, self.b1])[self.a1.get_id()], OneWaySyncSet([self.a1, self.b1])[self.a1.get_id()])
        self.assertEqual(OneWaySyncSet([self.a1, self.b1])[self.a1.get_id()], OneWaySyncSet([self.b1, self.a1])[self.a1.get_id()])
        self.assertEqual(OneWaySyncSet([self.b1, self.a1]), OneWaySyncSet([self.a1, self.b1]))

    def test_remove(self):
        self.myslave.add(self.a1)
        self.myslave.remove(self.a1)
        self.assertTrue(len(self.myslave) == 0)
        self.myslave.add(self.a1)
        self.myslave.remove(self.a2)
        self.assertTrue(len(self.myslave) == 0)
        self.myslave.add(self.a1)
        self.assertRaises(KeyError, self.myslave.remove, self.b1)

    def test_discard(self):
        self.myslave.add(self.a1)
        self.myslave.discard(self.a1)
        self.assertTrue(len(self.myslave) == 0)
        self.myslave.add(self.a1)
        self.myslave.discard(self.a2)
        self.assertTrue(len(self.myslave) == 0)
        self.myslave.discard(self.b1)
        self.assertTrue(len(self.myslave) == 0)

    def test_pop(self):
        self.myslave.add(self.a1)
        item = self.myslave.pop()
        self.assertTrue(len(self.myslave) == 0)
        self.assertEqual(id(item), id(self.a1))
        self.assertRaises(KeyError, self.myslave.pop)

    # Strictly dict functionality
    def test_keys(self):
        self.myslave.add(self.a1)
        self.assertEqual(self.myslave.keys(), [self.a1.get_id()])
        self.assertEqual(list(self.myslave.iterkeys()), [self.a1.get_id()])
        self.myslave.add(self.b1)
        self.myslave.add(self.c1)
        self.assertSetEqual(set(self.myslave.keys()), {self.a1.get_id(), self.b1.get_id(), self.c1.get_id()})
        self.assertSetEqual(set(self.myslave.iterkeys()), {self.a1.get_id(), self.b1.get_id(), self.c1.get_id()})

    # Boolean operators
    def test_isdisjoint(self):
        self.assertRaises(UndefinedBehaviorError, self.myslave.isdisjoint, self.mymaster)

    def test_issubset(self):
        self.assertRaises(UndefinedBehaviorError, self.myslave.issubset, self.mymaster)
        self.assertRaises(UndefinedBehaviorError, self.myslave.__le__, self.mymaster)

    def test_istruesubset(self):
        self.assertRaises(UndefinedBehaviorError, self.myslave.__lt__, self.mymaster)

    def test_issuperset(self):
        self.assertRaises(UndefinedBehaviorError, self.myslave.issuperset, self.mymaster)
        self.assertRaises(UndefinedBehaviorError, self.myslave.__ge__, self.mymaster)

    def test_istruesuperset(self):
        self.assertRaises(UndefinedBehaviorError, self.myslave.__gt__, self.mymaster)

    # Operators
    def test_union(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave.__or__(self.mymaster)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b1, data)
        self.assertIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave | self.mymaster
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b1, data)
        self.assertIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave.union(self.mymaster)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b1, data)
        self.assertIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b2])
        set1 = OneWaySyncSet([self.b1, self.c2])
        set2 = OneWaySyncSet([self.c1])
        data = self.myslave.union(set1, set2)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b1, data)
        self.assertIn(self.c1, data)

    def test_intersection(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave.__and__(self.mymaster)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.b1, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave & self.mymaster
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.b1, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave.intersection(self.mymaster)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.b1, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        set1 = OneWaySyncSet([self.a1, self.b2])
        set2 = OneWaySyncSet([self.a2, self.c1])
        data = self.myslave.intersection(set1, set2)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a2, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

    def test_difference(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave.__sub__(self.mymaster)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave - self.mymaster
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave.difference(self.mymaster)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

    def test_symmetric_difference(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c1])
        data = self.myslave.symmetric_difference(self.mymaster)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.c1, data)
        self.assertNotIn(self.b1, data)

    # In-place operators
    def test_update(self):
        self.myslave = OneWaySyncSet([self.a1])
        self.mymaster = OneWaySyncSet([self.b1])
        self.myslave.__ior__(self.mymaster)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1])
        self.mymaster = OneWaySyncSet([self.b1])
        self.myslave |= self.mymaster
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1])
        self.mymaster = OneWaySyncSet([self.b1])
        self.myslave.update(self.mymaster)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1])
        set1 = OneWaySyncSet([self.b1])
        set2 = OneWaySyncSet([self.c1])
        self.myslave.update(set1, set2)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertIn(self.b1, self.myslave)
        self.assertIn(self.c1, self.myslave)

    def test_intersection_update(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave.__iand__(self.mymaster)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.b1, self.myslave)
        self.assertNotIn(self.a1, self.myslave)
        self.assertNotIn(self.c3, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave &= self.mymaster
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.b1, self.myslave)
        self.assertNotIn(self.a1, self.myslave)
        self.assertNotIn(self.c3, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave.intersection_update(self.mymaster)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.b1, self.myslave)
        self.assertNotIn(self.a1, self.myslave)
        self.assertNotIn(self.c3, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        set1 = OneWaySyncSet([self.a1, self.b2])
        set2 = OneWaySyncSet([self.a1, self.c1])
        self.myslave.intersection_update(set1, set2)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertNotIn(self.b1, self.myslave)
        self.assertNotIn(self.c1, self.myslave)

    def test_difference_update(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave.__isub__(self.mymaster)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertNotIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave -= self.mymaster
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertNotIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave.difference_update(self.mymaster)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertNotIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1, self.c1])
        set1 = OneWaySyncSet([self.b1])
        set2 = OneWaySyncSet([self.c1])
        self.myslave.difference_update(set1, set2)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertNotIn(self.b1, self.myslave)
        self.assertNotIn(self.c1, self.myslave)

    def test_symmetric_difference_update(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave.__ixor__(self.mymaster)
        self.assertIsInstance(self.myslave, SyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertIn(self.c3, self.myslave)
        self.assertNotIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave ^= self.mymaster
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertIn(self.c3, self.myslave)
        self.assertNotIn(self.b1, self.myslave)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        self.mymaster = OneWaySyncSet([self.b1, self.c3])
        self.myslave.symmetric_difference_update(self.mymaster)
        self.assertIsInstance(self.myslave, OneWaySyncSet)
        self.assertIn(self.a1, self.myslave)
        self.assertIn(self.c3, self.myslave)
        self.assertNotIn(self.b1, self.myslave)

    # Diff tests
    def test_oneway_diff(self):
        for m in (self.a2, self.b2, self.c2):
            self.myslave.add(m)
        for m in (self.a1, self.b2, self.c3):
            self.mymaster.add(m)
        only_in_self, only_in_master, outdated_in_self, updated_in_master = self.myslave.diff(self.mymaster)
        for coll in (only_in_self, only_in_master, outdated_in_self, updated_in_master):
            self.assertIsInstance(coll, OneWaySyncSet)
        self.assertEqual(only_in_self, OneWaySyncSet())
        self.assertEqual(only_in_master, OneWaySyncSet())
        self.assertEqual(outdated_in_self, OneWaySyncSet([self.a2, self.c2]))
        self.assertEqual(updated_in_master, OneWaySyncSet([self.a1, self.c3]))

    def test_oneway_diff_2(self):
        for m in (self.a2, self.b1):
            self.myslave.add(m)
        for m in (self.c3, self.b2):
            self.mymaster.add(m)
        only_in_self, only_in_master, outdated_in_self, updated_in_master =  self.myslave.diff(self.mymaster)
        for coll in (only_in_self, only_in_master, outdated_in_self, updated_in_master):
            self.assertIsInstance(coll, OneWaySyncSet)
        self.assertEqual(only_in_self, OneWaySyncSet([self.a2]))
        self.assertEqual(only_in_master, OneWaySyncSet([self.c3]))
        self.assertEqual(outdated_in_self, OneWaySyncSet([self.b1]))
        self.assertEqual(updated_in_master, OneWaySyncSet([self.b2]))


class TwoWaySyncSetTest(_TwoWayBaseClass):
    def test_constructor(self):
        self.assertEqual(self.myset, self.otherset)
        self.assertEqual(self.myset.item_dict, self.otherset.item_dict)
        self.myset = TwoWaySyncSet([self.a1, self.b1, self.c1])
        self.otherset = TwoWaySyncSet([self.a1, self.b1, self.c1])
        self.assertEqual(self.myset, self.otherset)
        self.assertEqual(self.myset.item_dict, self.otherset.item_dict)
        self.otherset = TwoWaySyncSet([self.c1, self.a1, self.b1])
        self.assertEqual(self.myset, self.otherset)
        self.assertEqual(self.myset.item_dict, self.otherset.item_dict)
        self.assertEqual(TwoWaySyncSet([self.a2, self.a1]), TwoWaySyncSet([self.a1, self.a2]))
        self.assertTrue(TwoWaySyncSet([self.a2, self.a1]) == TwoWaySyncSet([self.a1, self.a2]))
        self.assertNotEqual(TwoWaySyncSet([self.a2, self.a1]), TwoWaySyncSet([self.a3, self.a1]))
        self.assertNotEqual(TwoWaySyncSet([self.a1, self.b1]), TwoWaySyncSet([self.a1, self.b2]))

    # Basic methods
    def test_copy(self):
        self.myset = TwoWaySyncSet([self.a1])
        set_copy = self.myset.copy()
        self.assertIsInstance(set_copy, TwoWaySyncSet)

    def test_add(self):
        for m in (self.a1, self.b1, self.c1):
            self.myset.add(m)
        self.assertEqual(len(self.myset), 3)
        self.assertEqual(self.myset[self.a1.get_id()], self.a1)
        self.assertNotEqual(self.myset[self.a1.get_id()], self.b1)
        self.assertNotEqual(self.myset[self.a1.get_id()], self.c1)
        self.assertEqual(self.myset[self.b1.get_id()], self.b1)
        self.assertEqual(self.myset[self.c1.get_id()], self.c1)

    def test_versions_add(self):
        # Also tests __getitem__
        for m in (self.a1, self.a2):
            self.myset.add(m)
        self.assertEqual(len(self.myset), 1)
        self.assertTrue(self.myset[self.a2.get_id()].__eq__(self.a1))
        self.assertEqual(self.myset[self.a2.get_id()].__cmp__(self.a2), 0)
        self.assertNotEqual(self.myset[self.a2.get_id()].__cmp__(self.a1), 0)

    def test_clear(self):
        for m in (self.a1, self.b3):
            self.myset.add(m)
        self.myset.clear()
        self.assertTrue(len(self.myset) == 0)

    def test_len(self):
        for m in (self.a1, self.a2):
            self.myset.add(m)
        self.assertTrue(len(self.myset) == 1)
        self.myset.add(self.b1)
        self.assertTrue(len(self.myset) == 2)

    # Basic operators
    def test_contains(self):
        self.myset.add(self.a1)
        self.assertIn(self.a1, self.myset)
        self.assertNotIn(self.a2, self.myset)
        self.assertNotIn(self.a3, self.myset)

    def test_contains_similar(self):
        self.myset.add(self.a1)
        self.assertTrue(self.myset.contains_similar(self.a1))
        self.assertTrue(self.myset.contains_similar(self.a2))
        self.assertFalse(self.myset.contains_similar(self.b1))

    def test_equal(self):
        self.assertEqual(TwoWaySyncSet([self.a1, self.b1])[self.a1.get_id()], TwoWaySyncSet([self.a1, self.b1])[self.a1.get_id()])
        self.assertEqual(TwoWaySyncSet([self.a1, self.b1])[self.a1.get_id()], TwoWaySyncSet([self.b1, self.a1])[self.a1.get_id()])
        self.assertEqual(TwoWaySyncSet([self.b1, self.a1]), TwoWaySyncSet([self.a1, self.b1]))

    def test_remove(self):
        self.myset.add(self.a1)
        self.myset.remove(self.a1)
        self.assertTrue(len(self.myset) == 0)
        self.myset.add(self.a1)
        self.myset.remove(self.a2)
        self.assertTrue(len(self.myset) == 0)
        self.myset.add(self.a1)
        self.assertRaises(KeyError, self.myset.remove, self.b1)

    def test_discard(self):
        self.myset.add(self.a1)
        self.myset.discard(self.a1)
        self.assertTrue(len(self.myset) == 0)
        self.myset.add(self.a1)
        self.myset.discard(self.a2)
        self.assertTrue(len(self.myset) == 0)
        self.myset.discard(self.b1)
        self.assertTrue(len(self.myset) == 0)

    def test_pop(self):
        self.myset.add(self.a1)
        item = self.myset.pop()
        self.assertTrue(len(self.myset) == 0)
        self.assertEqual(id(item), id(self.a1))
        self.assertRaises(KeyError, self.myset.pop)

    # Boolean operators
    def test_isdisjoint(self):
        self.assertRaises(UndefinedBehaviorError, self.myset.isdisjoint, self.otherset)

    def test_issubset(self):
        self.assertRaises(UndefinedBehaviorError, self.myset.issubset, self.otherset)
        self.assertRaises(UndefinedBehaviorError, self.myset.__le__, self.otherset)

    def test_istruesubset(self):
        self.assertRaises(UndefinedBehaviorError, self.myset.__lt__, self.otherset)

    def test_issuperset(self):
        self.assertRaises(UndefinedBehaviorError, self.myset.issuperset, self.otherset)
        self.assertRaises(UndefinedBehaviorError, self.myset.__ge__, self.otherset)

    def test_istruesuperset(self):
        self.assertRaises(UndefinedBehaviorError, self.myset.__gt__, self.otherset)

    # Operators
    def test_union(self):
        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c1])
        data = self.myset.__or__(self.otherset)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b1, data)
        self.assertIn(self.c1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c1])
        data = self.myset | self.otherset
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b1, data)
        self.assertIn(self.c1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c1])
        data = self.myset.union(self.otherset)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b1, data)
        self.assertIn(self.c1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b2])
        set1 = TwoWaySyncSet([self.b1, self.c2])
        set2 = TwoWaySyncSet([self.c1])
        data = self.myset.union(set1, set2)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.b2, data)
        self.assertIn(self.c2, data)

    def test_intersection(self):
        self.myslave = OneWaySyncSet([self.a1, self.b1])
        set1 = OneWaySyncSet([self.a2, self.c1])
        data = self.myslave.__and__(set1)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a2, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        set1 = OneWaySyncSet([self.a2, self.c1])
        data = self.myslave & set1
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a2, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        set1 = OneWaySyncSet([self.a2, self.c1])
        data = self.myslave.intersection(set1)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a2, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

        self.myslave = OneWaySyncSet([self.a1, self.b1])
        set1 = OneWaySyncSet([self.a1, self.b2])
        set2 = OneWaySyncSet([self.a2, self.c1])
        data = self.myslave.intersection(set1, set2)
        self.assertIsInstance(data, OneWaySyncSet)
        self.assertIn(self.a2, data)
        self.assertNotIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.b2, data)
        self.assertNotIn(self.c1, data)

    def test_difference(self):
        self.myset = TwoWaySyncSet([self.a1, self.b1])
        set1 = TwoWaySyncSet([self.b1])
        data = self.myset.__sub__(set1)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertNotIn(self.b1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        set1 = TwoWaySyncSet([self.b1])
        data = self.myset - set1
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertNotIn(self.b1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        set1 = TwoWaySyncSet([self.b1])
        data = self.myset.difference(set1)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertNotIn(self.b1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        set1 = TwoWaySyncSet([self.b1])
        set2 = TwoWaySyncSet([self.c1])
        data = self.myset.difference(set1, set2)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertNotIn(self.b1, data)
        self.assertNotIn(self.c1, data)

    def test_symmetric_difference(self):
        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c1])
        data = self.myset.__xor__(self.otherset)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.c1, data)
        self.assertNotIn(self.b1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c1])
        data = self.myset ^ self.otherset
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.c1, data)
        self.assertNotIn(self.b1, data)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c1])
        data = self.myset.symmetric_difference(self.otherset)
        self.assertIsInstance(data, TwoWaySyncSet)
        self.assertIn(self.a1, data)
        self.assertIn(self.c1, data)
        self.assertNotIn(self.b1, data)

    # In-place operators
    def test_update(self):
        self.myset = TwoWaySyncSet([self.a1])
        self.otherset = TwoWaySyncSet([self.b1])
        self.myset.__ior__(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1])
        self.otherset = TwoWaySyncSet([self.b1])
        self.myset |= self.otherset
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1])
        self.otherset = TwoWaySyncSet([self.b1])
        self.myset.update(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1])
        set1 = TwoWaySyncSet([self.b1])
        set2 = TwoWaySyncSet([self.c1])
        self.myset.update(set1, set2)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertIn(self.b1, self.myset)
        self.assertIn(self.c1, self.myset)

    def test_intersection_update(self):
        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset.__iand__(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.b1, self.myset)
        self.assertNotIn(self.a1, self.myset)
        self.assertNotIn(self.c3, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset &= self.otherset
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.b1, self.myset)
        self.assertNotIn(self.a1, self.myset)
        self.assertNotIn(self.c3, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset.intersection_update(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.b1, self.myset)
        self.assertNotIn(self.a1, self.myset)
        self.assertNotIn(self.c3, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        set1 = TwoWaySyncSet([self.a1, self.b2])
        set2 = TwoWaySyncSet([self.a1, self.c1])
        self.myset.intersection_update(set1, set2)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertNotIn(self.b1, self.myset)
        self.assertNotIn(self.c1, self.myset)

    def test_difference_update(self):
        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset.__isub__(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertNotIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset -= self.otherset
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertNotIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset.difference_update(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertNotIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1, self.c1])
        set1 = TwoWaySyncSet([self.b1])
        set2 = TwoWaySyncSet([self.c1])
        self.myset.difference_update(set1, set2)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertNotIn(self.b1, self.myset)
        self.assertNotIn(self.c1, self.myset)

    def test_symmetric_difference_update(self):
        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset.__ixor__(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertIn(self.c3, self.myset)
        self.assertNotIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset ^= self.otherset
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertIn(self.c3, self.myset)
        self.assertNotIn(self.b1, self.myset)

        self.myset = TwoWaySyncSet([self.a1, self.b1])
        self.otherset = TwoWaySyncSet([self.b1, self.c3])
        self.myset.symmetric_difference_update(self.otherset)
        self.assertIsInstance(self.myset, TwoWaySyncSet)
        self.assertIn(self.a1, self.myset)
        self.assertIn(self.c3, self.myset)
        self.assertNotIn(self.b1, self.myset)

    # Diff tests
    def test_twoway_diff(self):
        for m in (self.a2, self.b2, self.c2):
            self.myset.add(m)
        for m in (self.a1, self.b2, self.c3):
            self.otherset.add(m)
        only_in_self, only_in_other, newer_in_self, newer_in_other =  self.myset.diff(self.otherset)
        for coll in (only_in_self, only_in_other, newer_in_self, newer_in_other):
            self.assertIsInstance(coll, TwoWaySyncSet)
        self.assertEqual(only_in_self, TwoWaySyncSet())
        self.assertEqual(only_in_other, TwoWaySyncSet())
        self.assertEqual(newer_in_self, TwoWaySyncSet([self.a2]))
        self.assertEqual(newer_in_other, TwoWaySyncSet([self.c3]))

    def test_twoway_diff_2(self):
        m0 = TestMember(0, 1)
        m10 = TestMember(4, 1)
        for m in (self.a2, self.b1, m0):
            self.myset.add(m)
        for m in (self.a1, self.b2, m10):
            self.otherset.add(m)
        only_in_self, only_in_other, newer_in_self, newer_in_other =  self.myset.diff(self.otherset)
        for coll in (only_in_self, only_in_other, newer_in_self, newer_in_other):
            self.assertIsInstance(coll, TwoWaySyncSet)
        self.assertEqual(only_in_self, TwoWaySyncSet([m0]))
        self.assertEqual(only_in_other, TwoWaySyncSet([m10]))
        self.assertEqual(newer_in_self, TwoWaySyncSet([self.a2]))
        self.assertEqual(newer_in_other, TwoWaySyncSet([self.b2]))


if __name__ == '__main__':
    unittest.main()