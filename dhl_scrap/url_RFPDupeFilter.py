from scrapy.dupefilters import  RFPDupeFilter
import os


# Url save unused fingerprint
class SeenURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""

    def __init__(self, path=None):
        self.urls_seen = set()
        self.urls_seen_file=None
        RFPDupeFilter.__init__(self)
        if path:
            self.urls_seen_file = open(os.path.join(path, 'requests.json'), 'a+')
            self.urls_seen_file.seek(0)
            self.urls_seen.update(x.rstrip() for x in self.urls_seen_file)

    def request_seen(self, request):
        fp = request.url
        if fp in self.urls_seen:
            return True
        self.urls_seen.add(fp)
        if self.urls_seen_file:
            self.urls_seen_file.write(fp + os.linesep)
        return False

    def close(self, reason):
        if self.urls_seen_file:
            self.urls_seen_file.close()


# test
class SeenUrl(object):
    def __init__(self,path=None):
        self.urls=set()
        self.urls_file=None
        if path:
            self.urls_file=open(os.path.join(path,'urls_seen.json'),'a+')
            self.urls_file.seek(0)
            self.urls.update(x.rstrip() for x in self.urls_file)
    def request_seen(self,request):
        fp = request.url
        if fp in self.urls:
            return True
        self.urls.add(fp)
        if self.urls_file:
            self.urls_file.write(fp + os.linesep)

    def close(self,reason):
        if self.urls_file:
            self.urls_file.close()

