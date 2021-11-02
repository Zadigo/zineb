import unittest
from zineb.tests.spiders.items import SpiderWithMultiple, SpiderWithMultipleDomains

class TestSpiderWithMultipleModels(unittest.TestCase):
    def test_resolution(self):
        spider = SpiderWithMultiple()
        model1 = spider._temp_model_holder[0]
        model2 = spider._temp_model_holder[1]
        self.assertEqual(model1._cached_result.as_values(), {'url': ['https://www.iana.org/domains/example']})
        self.assertEqual(model2._cached_result.as_values(), {'value': ['More information...']})


class TestSpiderwithMultipleDomains(unittest.TestCase):
    def test_resolution(self):
        SpiderWithMultipleDomains()


if __name__ == '__main__':
    unittest.main()
