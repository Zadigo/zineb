from functools import lru_cache
import threading
from zineb.http.request import HTTPRequest

BAD_URLS = [
    'http://example.com',
    'http:///example.com',
    'https://example.com',
    'ftp://example.com',
    r'\\example.com',
    r'\\\example.com',
    r'/\\/example.com',
    r'\\\example.com',
    r'\\example.com',
    r'\\//example.com',
    r'/\/example.com',
    r'\/example.com',
    r'/\example.com',
    'http:///example.com',
    r'http:/\//example.com',
    r'http:\/example.com',
    r'http:/\example.com',
    'javascript:alert("XSS")',
    '\njavascript:alert(x)',
    '\x08//example.com',
    r'http://otherserver\@example.com',
    r'http:\\testserver\@example.com',
    r'http://testserver\me:pass@example.com',
    r'http://testserver\@example.com',
    r'http:\\testserver\confirm\me@example.com',
    'http:999999999',
    'ftp:9999999999',
    '\n',
    'http://[2001:cdba:0000:0000:0000:0000:3257:9652/',
    'http://2001:cdba:0000:0000:0000:0000:3257:9652]/'
]



@lru_cache(maxsize=10)
def create_test_request():
    request = HTTPRequest('http://example.com')
    request._send()
    return request


def create_test_requests(urls):
    requests = [HTTPRequest(url) for url in urls]

    results = []
    def wrapper(request):
        try:
            request._send()
        except:
            results.append(False)
        else:
            results.append(True)
            
    threads = [threading.Thread(target=wrapper, request=request) for request in requests]
    for thread in threads:
        thread.start()
    return results

create_test_requests(BAD_URLS)
