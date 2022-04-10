import asyncio
import unittest
from collections import namedtuple
from http.client import InvalidURL
from typing import Generator
from urllib.parse import ParseResult

import requests
from bs4 import BeautifulSoup
from requests.models import Response
from zineb.exceptions import ResponseFailedError
from zineb.http.headers import ResponseHeaders
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse
from zineb.tags import Link
from zineb.tests.http_clients.items import BAD_URLS, create_simple_request


class TeestBaseRequest(unittest.TestCase):
    def test_request_class(self):
        request = HTTPRequest
        self.assertFalse(request.can_be_sent)
        self.assertListEqual(request.http_methods, ['GET', 'POST'])
        
    def test_request_instance(self):
        request = HTTPRequest('http://example.com')
        # A request is considered safe
        # to be sent as is
        self.assertTrue(request.can_be_sent)
        self.assertIsNone(request._http_response)
        self.assertIsNone(request.html_response)
        self.assertIsInstance(request._url_meta, ParseResult)
        
    def test_global_http_api(self):
        request = create_simple_request(send=True)

        self.assertTrue(request.can_be_sent)
        
        self.assertEqual(request.url, 'http://example.com')
        self.assertIsNotNone(request.url)
        
        self.assertListEqual(request.errors, [])
        self.assertTrue(request.resolved)
        
        self.assertIsNotNone(request.html_response)
        self.assertIsInstance(request._http_response, Response)
    
    def test_domain_restriction(self):
        request = HTTPRequest('http://example.com')
        request.only_secured_requests = True
        request._send()

    def test_secured_requests(self):
        pass

    def test_link_following(self):       
        request = HTTPRequest('http://example.com')
        response = request.follow('http://example.com')
        
        self.assertIsInstance(response, HTMLResponse)
        self.assertEqual(response.cached_response.url, 'http://example.com/')
        self.assertEqual(response.page_title, 'Example Domain')
                
        # async def new_request():
        #     request = HTTPRequest('http://example.com')
        #     return request.follow('http://example.com')
        
        # async def send():
        #     response = await new_request()
        #     return response
        
        # result = asyncio.run(send())
        # print(result)
        
    def test_multiple_link_following(self):
        request = HTTPRequest('http://example.com')
        responses = request.follow_all(['http://example.com'])
        
        # Resolution of the the follow_all is deferred
        # until the user iterates over the generator
        self.assertIsInstance(responses, Generator)
        # self.assertEqual(response.cached_response.url, 'http://example.com/')
        # self.assertEqual(response.page_title, 'Example Domain')

        # tag = _request.html_response.html_page.find('a')
        # links = [Link(tag), Link(tag)]
        # responses = _request.follow_all(links)
        # self.assertIsInstance(responses, Generator)
        # self.assertEqual(len(list(responses)), 2)

    def test_headers(self):
        request = HTTPRequest('http://example.com')
        request._send()
        self.assertIsInstance(request.html_response.headers, ResponseHeaders)
        self.assertEqual(request.html_response.headers.get('x-cache'), 'HIT')
        
    def test_bad_urls(self):
        # FIXME: Test bad urls on the request
        for url in BAD_URLS:
            with self.subTest(url=url):
                request = HTTPRequest(url)
                with self.assertRaises(Exception):
                    request._send()
                self.assertFalse(request.can_be_sent)


if __name__ == '__main__':
    unittest.main()
