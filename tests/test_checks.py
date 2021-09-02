import os
import unittest

from zineb.settings import Settings
from zineb.checks.core import checks_registry
from zineb.exceptions import ImproperlyConfiguredError

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject.settings')

# Reload the settings file in order to
# load the user project settings
settings = Settings()

class TestApplicationChecks(unittest.TestCase):
    def setUp(self):
        checks_registry._default_settings = settings
        # checks_registry.run()

    @unittest.expectedFailure
    def test_spiders_is_not_a_list(self):
        checks_registry._default_settings['SPIDERS'] = None
        self.assertRaises(ValueError, checks_registry.run)

        checks_registry._default_settings['SPIDERS'] = 'Spider'
        self.assertRaises(ValueError, checks_registry.run)

    def test_middlewares_is_not_a_list(self):
        checks_registry._default_settings['MIDDLEWARES'] = 'Some middleware'
        self.assertRaises(ValueError, checks_registry.run)

    def test_user_agetns_is_not_a_list(self):
        checks_registry._default_settings['USER_AGENTS'] = 'User agent'
        self.assertRaises(ValueError, checks_registry.run)

    @unittest.expectedFailure
    def test_object_in_list_is_not_string(self):
        checks_registry._default_settings['MIDDLEWARES'] = [1, 2, 3]
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)

    @unittest.expectedFailure
    def test_default_request_haders(self):
        checks_registry._default_settings['DEFAULT_REQUEST_HEADERS'] = []
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)

    def test_proxies_are_not_valid(self):
        checks_registry._default_settings['PROXIES'] = [('some  value', '127.0.0.1')]
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)

        checks_registry._default_settings['PROXIES'] = [('http', 'who said that')]
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)


if __name__ == '__main__':
    unittest.main()
