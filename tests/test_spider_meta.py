import unittest

from zineb.tests.spiders import MetaSpider


class TestMeta(unittest.TestCase):
    def setUp(self):
        self.spider = MetaSpider()

    def test_spider_init(self):
        self.assertIsInstance(self.spider._meta, dict)
        self.assertDictEqual(dict(self.spider._meta), {'domains': ['example.com']})


if __name__ == '__main__':
    unittest.main()
