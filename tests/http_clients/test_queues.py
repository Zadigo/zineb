import unittest
from zineb.utils.queues import RequestQueue

class TestRequestQueue(unittest.TestCase):
    def setUp(self):
        self.queue = RequestQueue(None, 'http://example.com')  
    def test_can_resolve(self):
        results = self.queue.resolve_all()
        print(list(results))


if __name__ == '__main__':
    unittest.main()
