from datetime import date
import syncset


class SyncURL(syncset.SyncSetMember):
    def __init__(self, url, last_modified):
        self.url = url
        self.last_modified = last_modified

    def get_id(self):
        return self.url

    def get_changekey(self):
        return self.last_modified

    def __repr__(self):
        return self.__class__.__name__+repr((self.url, self.last_modified))


# URLs
foo = "http://mysrv/foo.html"
bar = "http://mysrv/bar.html"
baz = "http://mysrv/baz.html"

# My version
myurls = syncset.OneWaySyncSet()
myurls.add(SyncURL(foo, date(2012, 1, 1)))
myurls.add(SyncURL(bar, date(2011, 12, 8)))

# Server version
serverurls = syncset.OneWaySyncSet()
serverurls.add(SyncURL(foo, date(2012, 2, 1)))
serverurls.add(SyncURL(bar, date(2011, 12, 8)))
serverurls.add(SyncURL(baz, date(2012, 2, 15)))

only_in_self, only_in_master, outdated_in_self, updated_in_master = myurls.diff(serverurls)
print(only_in_self)
print(only_in_master)
print(outdated_in_self)
print(updated_in_master)

myurls.update(serverurls)
print(myurls)
