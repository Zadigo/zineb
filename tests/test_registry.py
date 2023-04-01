import os
import pathlib
import unittest
from importlib import import_module

from zineb.exceptions import SpiderExistsError
from zineb.middleware import Middleware
from zineb.registry import MasterRegistry, SpiderConfig
from zineb.settings import settings

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'tests.testproject')

settings()


class TestSpiderConfig(unittest.TestCase):
    def setUp(self):
        self.config = SpiderConfig(
            'MySpider',
            import_module('tests.testproject.spiders')
        )

    def test_global_options(self):
        self.assertTrue(self.config.name == 'MySpider')
        self.assertIsNotNone(self.config.path)
        self.assertTrue(pathlib.Path(self.config.path).is_dir())
        # Spider can only be ready after
        # check_ready is called
        self.assertFalse(self.config.is_ready)

    def test_can_run_spider_internally(self):
        self.config.check_ready()
        self.assertTrue(self.config.is_ready)
        self.config.run()


class TestMasterRegistry(unittest.TestCase):
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

    def test_registry_integrity(self):
        self.assertFalse(self.registry.is_ready)

        self.registry.populate()
        spiders = self.registry.get_spiders()

        self.assertTrue(self.registry.is_ready)
        self.assertTrue(len(spiders) > 0)
        self.assertTrue(self.registry.has_spider('MySpider'))
        self.assertIsInstance(
            self.registry.get_spider('MySpider'),
            SpiderConfig
        )
        self.assertIsInstance(self.registry.middlewares, Middleware)
        self.assertEqual(self.registry.project_name, 'testproject')
        self.assertTrue(pathlib.Path(self.registry.absolute_path).is_dir())

    @unittest.expectedFailure
    def test_error_spider_not_found(self):
        self.assertRaises(
            SpiderExistsError,
            self.registry.get_spider,
            'TestSpider'
        )


if __name__ == '__main__':
    unittest.main()
