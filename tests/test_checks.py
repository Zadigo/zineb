import os
import unittest

from zineb.checks.core import checks_registry
from zineb.exceptions import ImproperlyConfiguredError
from zineb.settings import settings

# Since checks require a project scope, set this
# to the default test one in order to avoid any errors
os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject')


# Reload the settings file in order to
# load the user project settings from the
# global variable above
settings_dict = settings()


class TestApplicationChecks(unittest.TestCase):        
    def test_spiders_is_not_a_list(self):
        settings(SPIDERS=None)
        self.assertRaises(ValueError, checks_registry.run)

        settings(SPIDERS='Spider')
        self.assertRaises(ValueError, checks_registry.run)
        
    def test_date_formats_is_invalid(self):
        # TODO: Content checks generate a ValueError
        # while integrity checks ImproperlyConfiguredError
        settings(DEFAULT_DATE_FORMATS='some dates')
        self.assertRaises(ValueError, checks_registry.run)
        
        settings(DEFAULT_DATE_FORMATS=[1])
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)
        
    def test_requires_dict(self):
        items = ['LOGGING', 'STORAGES', 'DEFAULT_REQUEST_HEADERS']
        
        for item in items:
            with self.subTest(item=item):
                settings(item='some invalid value')
                self.assertRaises(ImproperlyConfiguredError, checks_registry.run)
        
    def test_requires_list(self):
        items = ['SPIDERS', 'DOMAINS', 'MIDDLEWARES',
                 'USER_AGENTS', 'PROXIES', 'RETRY_HTTP_CODES',
                 'DEFAULT_DATE_FORMATS']
        
        for item in items:
            with self.subTest(item=item):
                settings(item='some invalid value')
                self.assertRaises(ImproperlyConfiguredError, checks_registry.run)

    def test_object_in_list_is_not_string(self):
        settings(MIDDLEWARES=[1, 2])
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)

    def test_proxies_are_not_valid(self):
        settings(PROXIES=[('some  value', '127.0.0.1')])
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)

        settings(PROXIES=[('http', 'who said that')])
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)
    
    def test_media_folder_is_not_string(self):
        settings(MEDIA_FOLDER=2)
        self.assertRaises(ImproperlyConfiguredError, checks_registry.run)


if __name__ == '__main__':
    unittest.main()
