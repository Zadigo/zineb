import unittest

from zineb.app import Zineb
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse
from bs4 import BeautifulSoup


class Spider(Zineb):
    start_urls = [
        'http://example.com'
    ]


class TestSpider(unittest.TestCase):
    def setUp(self):
        self.spider = Spider()

    def test_prepared_requests(self):
        http_response = self.spider.get_response(0)
        self.assertEqual(len(self.spider.prepared_requests), 1)
        self.assertIsInstance(http_response, HTTPRequest)
        self.assertEqual(http_response.url, 'http://example.com')

    def test_response_objects(self):
        http_request = self.spider.get_response(0)
        self.assertIsInstance(http_request.html_response, HTMLResponse)
        self.assertIsInstance(http_request.html_response.html_page, BeautifulSoup)
        self.assertTrue(http_request.resolved)

    def test_page_title(self):
        http_request = self.spider.get_response(0)
        self.assertEqual(http_request.html_response.page_title, 'Example Domain')


if __name__ == "__main__":
    unittest.main()
