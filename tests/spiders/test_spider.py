import unittest

from zineb.tests.spiders import items
from zineb.utils.iteration import RequestQueue


class TestSpider(unittest.TestCase):
    def setUp(self):
        self.spider = items.SimpleSpider(debug=True)

    def test_spider_setup(self):
        self.assertIsInstance(self.spider.start_urls, list)
        self.assertNotIsInstance(self.spider.meta.start_urls, RequestQueue)
        self.assertIsInstance(self.spider.meta.prepared_requests, RequestQueue)
        self.assertTrue(len(self.spider.start_urls) > 0)
        self.assertEqual(self.spider.meta.spider_name, 'simplespider')
        self.assertListEqual(self.spider.meta.domains, [])


if __name__ == '__main__':
    # # unittest.main()
    # runner = unittest.TextTestRunner()
    # suite = unittest.TestSuite()
    # suite.addTest(TestSpider('test_prepared_requests'))
    # # suite.addTest(TestSpider('test_response_objects'))
    # # suite.addTest(TestSpider('test_page_title'))
    # runner.run(suite)
    unittest.main()
