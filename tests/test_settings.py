import unittest
from importlib import import_module

from zineb.settings import LazySettings, Settings, UserSettings


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

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

    def test_user_settings_not_configured(self):
        # This should return False since we are not using
        # a manage.py file that sets a project path in the
        # environment variable e.g. project.settings
        self.assertFalse(self.settings._user_settings.configured)


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


if __name__ == '__main__':
    unittest.main()
