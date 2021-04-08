from zineb.settings import Settings, UserSettings, LazySettings
from importlib import import_module
import unittest



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

    @unittest.expectedFailure
    def test_user_settings_not_configured(self):
        # This should return False since we are not using
        # a manage.py file that sets a project path in the
        # environment variable e.g. project.settings
        self.assertTrue(self.settings._user_settings.configured)


class TestUserSettings(unittest.TestCase):
    def setUp(self):
        self.user_settings = UserSettings('zineb.tests._test_settings_file')

    def test_can_access_settings_attribute(self):
        _ = self.user_settings.PROJECT_PATH

    def test_module_path(self):
        self.assertEqual(self.user_settings.SETTINGS_MODULE, 'zineb.tests._test_settings_file')

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
