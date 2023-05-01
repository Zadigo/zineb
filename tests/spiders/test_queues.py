import unittest

from zineb.utils.iterations import RequestQueue


class TestRequestQueue(unittest.TestCase):
    def setUp(self):
        self.instance = RequestQueue('http://example.com')

    def test_can_create_requests(self):
        self.assertEqual(len(self.instance), 1)

    def test_can_resolve(self):
        self.instance.resolve_all()

    def test_can_get_item(self):
        from zineb.http.request import HTTPRequest
        self.assertIsInstance(self.instance['http://example.com'], HTTPRequest)


if __name__ == '__main__':
    unittest.main()
