import unittest
from typing import Generator
from urllib.parse import ParseResult
from zineb.settings import settings
from requests.models import Response

from zineb.http.headers import ResponseHeaders
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse
from zineb.tests.http_clients.items import BAD_URLS, create_simple_request


class TestBaseRequest(unittest.TestCase):
    def test_request_class(self):
        request = HTTPRequest
        self.assertTrue(request.can_be_sent)
        self.assertListEqual(request.http_methods, ['GET', 'POST'])

    def test_domains_flag(self):
        settings(DOMAINS=['http://google.com'])
        request = create_simple_request()
        self.assertFalse(request.can_be_sent)

    def test_https_flag(self):
        settings(ENSURE_HTTPS=True)
        request = create_simple_request()
        self.assertFalse(request.can_be_sent)
        
    def test_request_instance(self):
        request = create_simple_request()
        # A request is orginally considered
        # safe to be sent as is
        self.assertTrue(request.can_be_sent)
        self.assertIsNone(request._http_response)
        self.assertIsNone(request.html_response)
        self.assertFalse(request.only_secured_requests)
        self.assertIsInstance(request._url_meta, ParseResult)
        self.assertListEqual(request.http_methods, ['GET', 'POST'])
        self.assertTrue(request.url == 'http://example.com')
        self.assertIsInstance(request.url, str)
        self.assertIsNone(request.root_url, None)

    def test_global_http_api(self):
        request = create_simple_request(send=True)

        self.assertTrue(request.can_be_sent)        
        self.assertEqual(request.url, 'http://example.com')
        self.assertIsNotNone(request.url)
        self.assertListEqual(request.errors, [])
        self.assertTrue(request.resolved)
        self.assertIsNotNone(request.html_response)
        self.assertIsInstance(request._http_response, Response)

    def test_link_following(self):       
        request = HTTPRequest
        new_instance = request.follow('http://example.com')
        self.assertIsInstance(new_instance, HTTPRequest)
        self.assertEqual(new_instance.html_response.page_title, 'Example Domain')
        
    def test_multiple_link_following(self):
        request = HTTPRequest
        instances = request.follow_all(['http://example.com'])
        
        # Resolution of the the follow_all is deferred
        # until the user iterates over the generator
        self.assertIsInstance(instances, Generator)
        instances = list(instances)
        for instance in instances:
            with self.subTest(instance=instance):
                self.assertIsInstance(instance, HTTPRequest)

    def test_headers(self):
        request = HTTPRequest('http://example.com')
        request._send()
        self.assertIsInstance(request.html_response.headers, ResponseHeaders)
        self.assertEqual(request.html_response.headers.get('x-cache'), 'HIT')
        
    def test_bad_urls(self):
        # FIXME: Test bad urls on the request but does
        # not raise Exceptions
        for url in BAD_URLS:
            with self.subTest(url=url):
                request = HTTPRequest(url)
                with self.assertRaises(Exception):
                    request._send()
                self.assertFalse(request.can_be_sent)
                
    def test_json_property(self):
        request = HTTPRequest('https://jsonplaceholder.typicode.com/todos')
        request._send()
        self.assertIsInstance(request.json(), dict)


if __name__ == '__main__':
    unittest.main()
