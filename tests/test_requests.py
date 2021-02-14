import unittest
from collections import OrderedDict

from bs4 import BeautifulSoup
from requests.models import Response
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse

request = HTTPRequest('http://example.com')
request._send()


class TestRequest(unittest.TestCase):
    def test_parameters(self):
        self.assertIsNotNone(request.url)
        self.assertIsNotNone(request.html_response)

    def test_http_response(self):
        self.assertIsInstance(request.html_response.cached_response, Response)

    def test_html_response(self):
        self.assertIsInstance(request.html_response, HTMLResponse)
        self.assertIsInstance(request.html_response.html_page, BeautifulSoup)

    def test_headers(self):
        self.assertIsInstance(request.html_response.headers, OrderedDict)

    def test_follow_link(self):
        link = request.html_response.html_page.find('a')
        new_request = request.follow(link.attrs.get('href'))
        self.assertEqual(new_request.cached_response.url, 'https://www.iana.org/domains/reserved')
        self.assertEqual(new_request.page_title, 'IANA — IANA-managed Reserved Domains')

    def test_count_links_on_page(self):
        self.assertEqual(len(request.html_response.links), 1)

    def test_count_images_on_page(self):
        self.assertEqual(len(request.html_response.images), 0)

    def test_url_join(self):
        self.assertEqual(request.html_response.urljoin('kendall'), 'http://example.com/kendall')

if __name__ == "__main__":
    unittest.main()
