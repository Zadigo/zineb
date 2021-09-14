import os
import unittest

from zineb.settings import LazySettings, Settings, UserSettings


class TestSettingsNotConfigured(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_can_access_settings_attribute(self):
        _ = self.settings.PROJECT_PATH

    def test_is_subscriptable(self):
        _ = self.settings['PROJECT_PATH']

    def test_can_be_reloaded(self):
        _ = self.settings(MYSETTING='Kendall')
        self.assertEqual(self.settings.MYSETTING, 'Kendall')
        self.assertTrue(self.settings.has_setting('MYSETTING'))

    def test_can_change(self):
        self.settings.PROJECT_PATH = None
        self.assertIsNone(self.settings.PROJECT_PATH)

    def test_user_settings_not_configured(self):
        # This should return False since we are not using
        # a manage.py file that sets a project path in the
        # environment variable e.g. project.settings
        self.assertFalse(self.settings._user_settings.configured)


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
        os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject.settings')

        settings = Settings()
        self.assertListEqual(settings.SPIDERS, ['MySpider'])


class TestUserSettings(unittest.TestCase):
    def setUp(self):
        self.python_path = 'zineb.tests.testproject.settings'
        self.user_settings = UserSettings(self.python_path)

    def test_can_access_settings_attribute(self):
        _ = self.user_settings.PROJECT_PATH

    def test_module_path(self):
        module = self.user_settings.SETTINGS_MODULE
        self.assertEqual(module.__name__, self.python_path)

    def test_is_configured(self):
        self.assertTrue(self.user_settings.configured)


class TestLazySettings(unittest.TestCase):
    def setUp(self):
        self.settings = LazySettings()

    def test_can_access_settings_attribute(self):
        _ = self.settings.PROJECT_PATH

    def test_is_subscriptable(self):
        _ = self.settings['PROJECT_PATH']

    def test_can_be_reloaded(self):
        _ = self.settings(MYSETTING='Kendall')
        self.assertEqual(self.settings.MYSETTING, 'Kendall')

    def test_can_change(self):
        self.settings.PROJECT_PATH = None
        self.assertIsNone(self.settings.PROJECT_PATH)


class TestUserSettings(unittest.TestCase):
    def setUp(self):
        user_settings = UserSettings('zineb.tests.testproject.settings')
        self.assertTrue(user_settings.is_configured)


if __name__ == '__main__':
    unittest.main()
