import unittest

from zineb.http.request import HTTPRequest
from zineb.middleware import Middleware
from zineb.settings import settings

global_settings = settings(PROXIES=[('http', '181.236.221.138:4145')])

middlewares = Middleware()


class TestMiddleware(unittest.TestCase):
    def test_loading(self):
        self.assertTrue(len(middlewares.middlewares.values()) > 0)
        self.assertIsInstance(middlewares.middlewares, dict)

    def test_call_function(self):
        middleware = middlewares.middlewares.get('RotatingProxy')
        self.assertTrue(callable(middleware))

    def test_get_middleware(self):
        middleware = middlewares.middlewares.get('RotatingProxy')
        request = HTTPRequest('http://example.com')
        # Call the middleware in order to test
        # whether it can be executed correctly
        middleware(request)
        self.assertDictEqual(request._proxy, {'http': '181.236.221.138:4145'})


if __name__ == '__main__':
    unittest.main()
