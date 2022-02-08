import unittest

from bs4 import BeautifulSoup
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse
from zineb.tests.spiders import items


class TestSpider(unittest.TestCase):
    def setUp(self):
        self.spider = items.SimpleSpider()

    def test_spider(self):
        # Test response
        self.assertEqual(len(self.spider._prepared_requests), 1)

        # Test response objects
        # http_request = self.spider._prepared_requests[0]
        # self.assertIsInstance(http_request.html_response, HTMLResponse)
        # self.assertIsInstance(http_request.html_response.html_page, BeautifulSoup)
        # self.assertTrue(http_request.resolved)

        # Test page title
        # http_request = self.spider._prepared_requests[0]
        # self.assertEqual(http_request.html_response.page_title, 'Example Domain')


class TestSpiderWithMeta(unittest.TestCase):
    def setUp(self):
        self.spider = items.MetaSpider()
        
    def test_used_with_valid_options(self):
        pass


if __name__ == '__main__':
#     # # unittest.main()
#     # runner = unittest.TextTestRunner()
#     # suite = unittest.TestSuite()
#     # suite.addTest(TestSpider('test_prepared_requests'))
#     # # suite.addTest(TestSpider('test_response_objects'))
#     # # suite.addTest(TestSpider('test_page_title'))
#     # runner.run(suite)
    unittest.main()
