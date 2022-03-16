import unittest
from typing import Generator

import requests
from bs4 import BeautifulSoup
from requests.models import Response
from zineb.http.headers import ResponseHeaders
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse
from zineb.tags import Link
from zineb.tests.http_clients.items import BAD_URLS, create_simple_request


class TeestBaseRequest(unittest.TestCase):
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

#     def test_link_following(self):
#         response = _request.follow(_request.html_response.links[0])
#         self.assertIsInstance(response, HTMLResponse)
        
#         self.assertEqual(response.cached_response.url, 'http://www.iana.org/domains/reserved')
#         self.assertEqual(response.page_title, 'IANA — IANA-managed Reserved Domains')


#     def test_multiple_link_following(self):
#         tag = _request.html_response.html_page.find('a')
#         links = [Link(tag), Link(tag)]
#         responses = _request.follow_all(links)
#         self.assertIsInstance(responses, Generator)
#         self.assertEqual(len(list(responses)), 2)

#     def test_headers(self):
#         self.assertIsInstance(_request.html_response.headers, ResponseHeaders)


# class TestHTTPRequest(unittest.TestCase):
#     def test_cached_response(self):
#         self.assertIsInstance(_request.html_response.cached_response, Response)

#     def test_html_response(self):
#         self.assertIsInstance(_request.html_response, HTMLResponse)
#         self.assertIsInstance(_request.html_response.html_page, BeautifulSoup)

#     def test_count_links_on_page(self):
#         self.assertEqual(len(_request.html_response.links), 1)

#     def test_count_images_on_page(self):
#         self.assertEqual(len(_request.html_response.images), 0)

#     def test_url_join(self):
#         self.assertEqual(_request.html_response.urljoin('kendall'), 'http://example.com/kendall')

if __name__ == '__main__':
    unittest.main()
