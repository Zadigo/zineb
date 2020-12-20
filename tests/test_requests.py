import unittest
from requests.models import Response
from bs4 import BeautifulSoup
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse

request = HTTPRequest('http://example.com')
request._send()

class TestField(unittest.TestCase):
    def test_parameters(self):
        self.assertIsNotNone(request.url)
        self.assertIsNotNone(request.html_response)

    def test_http_response(self):
        self.assertIsInstance(request.html_response.cached_response, Response)

    def test_html_response(self):
        self.assertIsInstance(request.html_response, HTMLResponse)
        self.assertIsInstance(request.html_response.html_page, BeautifulSoup)

    def test_follow_link(self):
        link = request.html_response.html_page.find('a')
        new_request = request.follow(link.attrs.get('href'))
        self.assertEqual(new_request.url, 'https://www.iana.org/domains/example')
        self.assertEqual(new_request.html_response.page_title, 'IANA — IANA-managed Reserved Domains')
        print(new_request.referer)
        # self.assertEqual(new_request.referer, 'http://example.com')

if __name__ == "__main__":
    unittest.main()
