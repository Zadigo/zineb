from functools import cached_property, lru_cache
from models.fields import DateField

from bs4 import BeautifulSoup
from zineb.http.request import HTTPRequest
from zineb.models.datastructure import Model
from zineb.models import fields

@lru_cache(maxsize=10)
def create_test_request() -> HTTPRequest:
    request = HTTPRequest('http://example.com')
    request._send()
    return request


def create_test_image_request() -> HTTPRequest:
    request = HTTPRequest('https://picsum.photos/200')
    request._send()
    return request


@lru_cache(maxsize=5)
def file_opener(path):
    with open(path, mode='r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    return soup


class TestModel(Model):
    age = fields.IntegerField()

test_model = TestModel()
