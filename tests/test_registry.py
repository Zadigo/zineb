import os
import unittest
from importlib import import_module

from zineb.exceptions import SpiderExistsError
from zineb.registry import MasterRegistry, SpiderConfig
from zineb.settings import settings

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject')

settings()


class TestSpiderConfig(unittest.TestCase):
    def setUp(self):
        self.config = SpiderConfig(
            'MySpider',
            import_module('zineb.tests.testproject.spiders')
        )

    def test_can_run_spider_internally(self):
        self.config.check_ready()
        self.assertTrue(self.config.is_ready)
        self.config.run()


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = MasterRegistry()

    def test_can_populate(self):
        self.registry.populate()
        self.assertTrue(self.registry.has_spiders)
        self.assertTrue(self.registry.is_ready)
        self.assertTrue(self.registry.has_spider('MySpider'))

    def test_can_get_spider(self):
        self.registry.populate()
        spider = self.registry.get_spider('MySpider')
        self.assertIsNotNone(spider)
        self.assertIsInstance(spider, SpiderConfig)
        self.assertTrue(self.registry.is_ready)
        
    @unittest.expectedFailure
    def test_error_spider_not_found(self):
        self.assertRaises(SpiderExistsError, self.registry.get_spider, 'TestSpider')

if __name__ == '__main__':
    unittest.main()

# registry = MasterRegistry()
# registry.populate()
# registry.populate()
# spider_config = registry.get_spider('MySpider')
# print(registry.check_spiders_ready())
# spider_config.run()
