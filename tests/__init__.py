from functools import lru_cache

from zineb.http.request import HTTPRequest, JsonRequest


@lru_cache(maxsize=10)
def ceate_test_request():
    request = HTTPRequest('http://example.com')
    request._send()
    return request

def create_test_json_request() -> JsonRequest:
    request = JsonRequest('https://jsonplaceholder.typicode.com/comments')
    request._send()
    return request
