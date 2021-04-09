import unittest

from zineb.middleware import Middleware
from zineb.settings import settings as global_settings


class TestMiddleware(unittest.TestCase):
    def setUp(self):
        self.middleware = Middleware(settings=global_settings)
        self.middleware._load

    def test_loading(self):
        self.assertTrue(len(self.middleware.loaded_middlewares) > 0)
        self.assertIsInstance(self.middleware.loaded_middlewares, dict)

    def test_call_function(self):
        self.assertTrue(callable(self.middleware.loaded_middlewares.get('Handler')))

    def test_get_middleware(self):
        middleware = self.middleware.get_middleware('History')
        self.assertTrue(callable(middleware))

    def test_has_modules(self):
        self.assertTrue(len(self.middleware.MODULES.keys()) > 0)

if __name__ == "__main__":
    unittest.main()
