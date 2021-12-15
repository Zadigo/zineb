from collections import defaultdict
from typing import Callable, OrderedDict, Type, Union

from zineb.http.request import HTTPRequest
from zineb.settings import lazy_settings
from zineb.utils.iteration import keep_while


class RequestQueue:
    """A class that takes and abstracts all the the
    starting urls of a spider"""
    
    request_queue = OrderedDict()
    history = defaultdict(dict)
    
    def __init__(self, spider: Callable, *urls, **request_params):
        self.spider = spider
        if not urls:
            urls = spider.start_urls
        self.url_strings = list(urls)
        
        self.request_queue
        for i, url in enumerate(self.url_strings):
            self.request_queue[url] = HTTPRequest(url, counter=i, **request_params)
            
    def __repr__(self):
        return f"{self.__class__.__name__}({dict(self.request_queue)})"
            
    def __iter__(self):
        return iter(self.request_queue)
    
    def __len__(self):
        return len(self.request_queue)
    
    def __enter__(self, *args, **kwargs):
        return self.request_queue
    
    def __exit__(self, *args, **kwargs):
        return False
    
    def __getitem__(self, url):
        return self.request_queue[url]
    
    def __delitem__(self, url):
        return self.request_queue.pop(url)
    
    def __contains__(self, url):
        return url in self.urls
    
    def __add__(self, instance):
        if not isinstance(instance, RequestQueue):
            raise TypeError('Instance should be an instance of RequestQueue')
        self_urls = self.urls
        self_urls.extend(instance.urls)
        return RequestQueue(self.spider, *self_urls)
    
    @property
    def has_urls(self):
        return len(self.urls) > 0
    
    @property
    def requests(self):
        return list(self.request_queue.items())
    
    @property
    def urls(self):
        return list(self.request_queue.keys())
    
    @property
    def unresolved_requests(self):
        return keep_while(lambda x: not x[1].resolved, self.request_queue.items())
    
    @property
    def failed_requests(self):
        return keep_while(lambda x: x['failed'], self.history.items())
    
    def get(self, url):
        return self.request_queue[url]
    
    def has_url(self, url):
        return url in self.request_queue.keys()
    
    def resolve_all(self):
        for url, request in self.request_queue.items():
            try:
                request._send()
            except:
                self.history[url].update({'failed': True, 'resolved': request.resolved})
            else:
                self.history[url].update({'failed': False, 'resolved': request.resolved})
                
    def retry_if_set(self):
        for url, instance in self.failed_requests:
            pass