class SpiderMeta(Zineb):
    start_urls = [
        'http://example.com'
    ]

    class Meta:
        domains = [
            'http://example.com'
        ]


class TestMeta(unittest.TestCase):
    def setUp(self):
        self.spider = SpiderMeta()

    def test_spider_init(self):
        self.assertIsInstance(self.spider._meta, dict)
        self.assertDictEqual(self.spider._meta, {
                             'domains': ['http://example.com']})
