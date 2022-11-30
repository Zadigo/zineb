# TODO:
import unittest

from zineb.middleware import Middleware
from zineb.settings import settings

global_settings = settings(MIDDLEWARES=['zineb.middlewares.history.History'])

middlewares = Middleware()


class TestMiddleware(unittest.TestCase):
    def test_loading(self):
        self.assertTrue(len(middlewares.loaded_middlewares) > 0)
        self.assertIsInstance(middlewares.loaded_middlewares, dict)

    def test_call_function(self):
        self.assertTrue(callable(middlewares.loaded_middlewares.get('History')))

    def test_get_middleware(self):
        middleware = middlewares.get_middleware('History')
        self.assertTrue(callable(middleware))

        # Call the middleware in order to test
        # whether it can be executed correctly
        middlewares(self)

    def test_has_modules(self):
        self.assertTrue(len(middlewares.MODULES.keys()) > 0)


if __name__ == '__main__':
    unittest.main()
