import unittest
from zineb.utils.iterations import RequestQueue


class TestRequestQueue(unittest.TestCase):
    def setUp(self):
        mockup_spider = type('Spider', (), {'meta': type(
            'SpiderOptions', (), {'domains': []})})
        urls = [
            'http://example.com',
            'https://jsonplaceholder.typicode.com/todos',
            'https://jsonplaceholder.typicode.com/posts',
            'https://data.opendatasoft.com/api/records/1.0/search/?dataset=fr-esr-principaux-etablissements-enseignement-superieur%40mesr&q=&facet=type_d_etablissement&facet=siren',
            'https://data.opendatasoft.com/api/records/1.0/search/?dataset=reseau-hta%40enedis&q='
        ]
        instance = RequestQueue(*urls)
        instance.prepare(mockup_spider)
        self.instance = instance

    def test_preparation_result(self):
        self.assertEqual(len(self.instance.request_queue.values()), 5)

    def test_asynchronous_iteration(self):
        responses = self.instance._iter()
        for response in responses:
            with self.subTest(response=response):
                self.assertTrue(response.resolved)
        self.assertEqual(responses, 5)


if __name__ == '__main__':
    unittest.main()
