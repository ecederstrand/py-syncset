import syncset 

class DemoMember(syncset.SyncSetMember):
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

print 'First, model a local read-only checkout that needs to be updated'
slave = syncset.OneWaySyncSet()
master = syncset.OneWaySyncSet()

slave.add(DemoMember('foo.py', 'r1'))
slave.add(DemoMember('bar.py', 'r1'))

master.add(DemoMember('foo.py', 'r2'))
master.add(DemoMember('bar.py', 'r3'))

print 'My outdated checkout:'
print slave
print 'The up-to-date repo:'
print master
print 'Updating the checkout:'
slave.update(master)
print slave

print
print 'Next, model a checkout with write-access to the repo'
mycopy = syncset.TwoWaySyncSet()
repo = syncset.OneWaySyncSet()

mycopy.add(DemoMember('foo.py', 'r1'))
mycopy.add(DemoMember('bar.py', 'r4'))

repo.add(DemoMember('foo.py', 'r2'))
repo.add(DemoMember('bar.py', 'r3'))

print 'My checkout with one file that I have changed (bar.py):'
print mycopy
print 'The repo with one file that someone else has changed (foo.py):'
print repo

#slave.diff(master)

print 'Updating my checkout without touching ny local change:'
mycopy.update(repo)
print mycopy
print 'Committing my changed file to the repo:'
repo.update(mycopy)
print repo
