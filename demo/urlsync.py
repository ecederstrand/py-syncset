from datetime import datetime
import syncset

class SyncURL(syncset.SyncSetMember):
   def __init__(self, url, last_modified):
      self.url = url
      self.last_modified = last_modified

   def get_id(self): return self.url
   def get_changekey(self): return self.last_modified
   def __repr__(self): return self.__class__.__name__+repr((self.url, self.last_modified))

# URLs
foo = "http://example.com/foo.html"
bar = "http://example.com/bar.html"
baz = "http://example.com/baz.html"

#My version 
myurls = syncset.OneWaySyncSet()
myurls.add(SyncURL(foo, datetime(2012, 1, 1, 11, 30, 2)))
myurls.add(SyncURL(bar, datetime(2011, 8, 1, 17, 23, 2)))
myurls.add(SyncURL(baz, datetime(2012, 2, 1, 9, 12, 3)))

# Server version
serverurls = syncset.OneWaySyncSet()
serverurls.add(SyncURL(foo, datetime(2012, 2, 1, 9, 12, 23)))
serverurls.add(SyncURL(bar, datetime(2011, 12, 8, 2, 6, 18)))
serverurls.add(SyncURL(baz, datetime(2012, 2, 1, 9, 12, 3)))

print myurls.diff(serverurls)

print myurls.update(serverurls)
