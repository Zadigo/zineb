from zineb.utils.queues import RequestQueue
import unittest


class TestRequestQueue(unittest.TestCase):
    def setUp(self):
        self.instance = RequestQueue(None, 'http://example.com')
        
    def test_can_create_requests(self):
        self.assertEqual(len(self.instance), 1)
        
    def test_can_resolve(self):
        self.instance.resolve_all()
                
        

if __name__ == '__main__':
    unittest.main()
