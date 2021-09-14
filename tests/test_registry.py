import os
import unittest
from importlib import import_module

from zineb.exceptions import SpiderExistsError
from zineb.registry import Registry, SpiderConfig
from zineb.settings import settings

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject.settings')

project_settings = settings()

class TestSpiderConfig(unittest.TestCase):
    def setUp(self):
        self.config = SpiderConfig(
            'testproject.spiders.MySpider',
            import_module('zineb.tests.testproject.spiders')
        )

    def test_can_get_spider(self):
        spider = self.config.get_spider('MySpider')
        self.assertIsNotNone(spider)

    def test_error_spider_not_found(self):
        self.assertRaises(SpiderExistsError, self.config.get_spider, 'TestSpider')

    def test_can_run_spider_internally(self):
        self.config.run()


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = Registry()

    def test_can_populate(self):
        self.registry.populate(
            import_module('zineb.tests.testproject.spiders')
        )
        self.assertTrue(self.registry.has_spiders)


if __name__ == '__main__':
    unittest.main()
