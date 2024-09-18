import os
import unittest

import zineb
from zineb.registry import registry
from zineb.settings import settings

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'tests.testproject')

zineb.setup()


class TestSetup(unittest.TestCase):
    def test_settings(self):
        self.assertIsNotNone(settings.PROJECT_PATH)

    def test_spiders(self):
        self.assertIsNotNone(settings.SPIDERS)

    def test_registry(self):
        self.assertTrue(registry.is_ready)
        self.assertTrue(registry.spiders_ready)
        self.assertFalse(registry.models_ready)


if __name__ == '__main__':
    unittest.main()
