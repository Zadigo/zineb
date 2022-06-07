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


# TODO: DELETE
# class TestHistoryMiddleware(unittest.TestCase):
#     def setUp(self):
#         self.middleware = middlewares.get_middleware('History')
#         self.middleware(self, url='http://example.com', tag='request')
    
#     def test_compiled_statistics(self):
#         result = self.middleware.compile_statistics()
#         self.assertEqual(result.count, 1)

#         requests = list(result.requests)
#         self.assertGreaterEqual(len(requests), 1)

#         # Result should be [('request', timestamp, url, token)]
#         request_information = requests[0]
#         self.assertIsInstance(request_information, (list, tuple ))
#         self.assertEqual(len(request_information), 4)
#         self.assertIn('request', request_information)


if __name__ == "__main__":
    unittest.main()
