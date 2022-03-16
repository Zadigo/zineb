import unittest
from zineb.utils.iteration import RequestQueue

class TestRequestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = RequestQueue('http://example.com')
        
    def test_can_resolve(self):
        results = self.queue.resolve_all()
        for result in results:
            with self.subTest(result=result):
                url, instance = result
                self.assertTrue(instance.resolved)


if __name__ == '__main__':
    unittest.main()
