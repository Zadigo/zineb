import os
import unittest

from zineb.settings import LazySettings, Settings, UserSettings

TEST_PROJECT_PYTHON_PATH = 'zineb.tests.testproject.settings'

class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_can_access_settings_attribute(self):
        result = self.settings.PROJECT_PATH
        self.assertIsNone(result)

    def test_is_subscriptable(self):
        result = self.settings['PROJECT_PATH']
        self.assertIsNone(result)

    def test_can_be_reloaded(self):
        instance = self.settings(MYSETTING='Kendall')
        self.assertEqual(self.settings.MYSETTING, 'Kendall')
        self.assertTrue(self.settings.has_setting('MYSETTING'))

    def test_can_change(self):
        self.settings.PROJECT_PATH = 'some/path'
        self.assertEqual(self.settings.PROJECT_PATH, 'some/path')

    def test_user_settings_not_configured(self):
        # This should return False since we are not using
        # manage.py which sets a project path in the
        # environment variable e.g. project.settings
        self.assertFalse(self.settings._user_settings.configured)
        
    def test_can_get_setting_with_prefix(self):
        self.settings['AWS_TEST1'] = None
        self.settings['AWS_TEST2'] = None
        result = self.settings.filter_by_prefix('AWS')
        self.assertDictEqual(result, {'AWS_TEST1': None, 'AWS_TEST2': None})


class TestSettingsNotConfigured(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_user_settings_configured_after_reload(self):
        # When the Settings() class is first configured,
        # it is done without the user's settings because
        # the environment variable ZINEB_SPIDER_PROJECT
        # is not yet set (this is true when the settings
        # file is called outside of the cmd).
        # By calling and therefore reloading settings
        # after setting the environment variable, a
        # new instance of settings is reloaded using
        # the user personalized settings.
        # That's why we have to load settings twice.

        # This becomes false when using the cmd to
        # call the project because the first thing
        # that is set in manage.py is the
        # environment variable.
        self.assertListEqual(self.settings.SPIDERS, [])
        os.environ.setdefault('ZINEB_SPIDER_PROJECT', TEST_PROJECT_PYTHON_PATH)

        settings = Settings()
        self.assertListEqual(settings.SPIDERS, ['MySpider'])


class TestUserSettings(unittest.TestCase):
    def setUp(self):
        self.user_settings = UserSettings(TEST_PROJECT_PYTHON_PATH)

    def test_can_access_settings_attribute(self):
        result = self.user_settings.PROJECT_PATH
        self.assertIsNotNone(result)

    def test_module_path(self):
        # Check that the module path corresponds
        # to what was above
        module = self.user_settings.SETTINGS_MODULE
        self.assertEqual(module.__name__, TEST_PROJECT_PYTHON_PATH)

    def test_is_configured(self):
        self.assertTrue(self.user_settings.configured)


class TestLazySettings(unittest.TestCase):
    def setUp(self):
        self.settings = LazySettings()

    def test_can_access_settings_attribute(self):
        result = self.settings.PROJECT_PATH
        self.assertIsNone(result)

    def test_is_subscriptable(self):
        result = self.settings['PROJECT_PATH']
        self.assertIsNone(result)

    def test_can_be_reloaded(self):
        result = self.settings(MYSETTING='Kendall')

    def test_can_change(self):
        self.settings.PROJECT_PATH = 'some/path'
        self.assertEqual(self.settings.PROJECT_PATH, 'some/path')


if __name__ == '__main__':
    unittest.main()
