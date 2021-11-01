from zineb.app import Zineb, Spider

class SpiderSubclass(Spider):
    start_urls = ['http://example.com']
    

class SimpleSpider(Zineb):
    start_urls = ['http://example.com']



class MetaSpider(Zineb):
    class Meta:
        domains = ['example.com']
