import os
import unittest

from zineb.checks.core import checks_registry
from zineb.exceptions import ImproperlyConfiguredError
from zineb.settings import settings


os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject.settings')


# Reload the settings file in order to
# load the user project settings from the
# global variable above
settings = settings()


class TestApplicationChecks(unittest.TestCase):
    @unittest.expectedFailure
    def test_spiders_is_not_a_list(self):
        checks_registry._default_settings['SPIDERS'] = None
        self.assertRaises(ValueError, checks_registry.run)

        checks_registry._default_settings['SPIDERS'] = 'Spider'
        self.assertRaises(ValueError, checks_registry.run)

    def test_middlewares_is_not_a_list(self):
        checks_registry._default_settings['MIDDLEWARES'] = 'Some middleware'
        self.assertRaises(ValueError, checks_registry.run)

    def test_user_agents_is_not_a_list(self):
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
