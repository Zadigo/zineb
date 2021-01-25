import unittest
from unittest.case import TestCase

from bs4 import BeautifulSoup
from zineb.app import Zineb
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse


class Spider(Zineb):
    start_urls = [
        'http://example.com'
    ]


class SpiderMeta(Zineb):
    start_urls = [
        'http://example.com'
    ]

    class Meta:
        domains = [
            'http://example.com'
        ]


class TestSpider(unittest.TestCase):
    def setUp(self):
        self.spider = Spider()

    def test_prepared_requests(self):
        http_response = self.spider._prepared_requests[0]
        self.assertEqual(len(self.spider._prepared_requests), 1)
        self.assertIsInstance(http_response, HTTPRequest)
        self.assertEqual(http_response.url, 'http://example.com')

    def test_response_objects(self):
        http_request = self.spider._prepared_requests[0]
        self.assertIsInstance(http_request.html_response, HTMLResponse)
        self.assertIsInstance(http_request.html_response.html_page, BeautifulSoup)
        self.assertTrue(http_request.resolved)

    def test_page_title(self):
        http_request = self.spider._prepared_requests[0]
        self.assertEqual(http_request.html_response.page_title, 'Example Domain')


class TestMeta(unittest.TestCase):
    def setUp(self):
        self.spider = SpiderMeta()

    def test_spider_init(self):
        self.assertIsInstance(self.spider._meta, dict)
        self.assertDictEqual(self.spider._meta, {'domains': ['http://example.com']})

if __name__ == "__main__":
    # unittest.main()
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(TestSpider('test_prepared_requests'))
    # suite.addTest(TestSpider('test_response_objects'))
    # suite.addTest(TestSpider('test_page_title'))
    runner.run(suite)
