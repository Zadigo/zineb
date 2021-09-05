import unittest

from bs4 import BeautifulSoup
from zineb.extractors.base import ImageExtractor, LinkExtractor, TableExtractor
from zineb.tags import ImageTag

# with open('tests/html/images.html', 'r') as f:
#     soup = BeautifulSoup(f, 'html.parser')


# with open('tests/html/tables2.html', 'r') as f:
#     soup2 = BeautifulSoup(f, 'html.parser')
#     tables = soup2.find_all('table')
#     player_table = None
#     for table in tables:
#         if table.has_attr('width'):
#             width = table.attrs.get('width')
#             if width == '631':
#                 player_table = table
    

# class TestImagesExtractor(unittest.TestCase):
#     extractor_class = ImageExtractor

#     def test_image_extraction(self):
#         extractor = self.extractor_class()
#         images = extractor.resolve(soup)
#         self.assertGreater(len(images), 0)
#         image = images[0]
#         self.assertIsInstance(image, ImageTag)

#     def test_filtering(self):
#         extractor = self.extractor_class(url_must_contain='Ambrosio')
#         images = extractor.resolve(soup)

#         filtered_images = extractor.filter_images()
#         self.assertNotEqual(len(images), len(filtered_images))

#         filtered_images = extractor.filter_images('901')
#         self.assertIn('Alessandra-Ambrosio-Booty-in-Bikini-901.jpg', filtered_images[0])


# class TestLinkExactor(unittest.TestCase):
#     def setUp(self):
#         extractor = LinkExtractor()
#         extractor.resolve(soup)
#         self.extractor = extractor

#     def test_can_be_used_with_context_processor(self):
#         with self.extractor as links:
#             self.assertTrue(len(links) > 1)

#     def test_can_iterate(self):
#         for _ in self.extractor:
#             pass

#     def test_contains(self):
#         self.assertFalse('google' in self.extractor)
#         self.assertTrue('https://www.sawfirst.com/' in self.extractor)

#     def test_can_add(self):
#         extractor2 = self.extractor()
#         extractor2.resolve(soup2)
#         result = self.extractor + extractor2
#         self.assertTrue(len(result) > 1)


with open('tests/html/tables3.html', mode='r') as f:
    tables = BeautifulSoup(f, 'html.parser')


def simple_processor(row):
    row[0] = 'changed'
    return row


class TestTableExtactor(unittest.TestCase):
    def setUp(self):
        extractor = TableExtractor()
        extractor.resolve(tables)

        self.extractor = extractor

    def test_has_values(self):
        self.assertTrue(len(self.extractor.values) > 0)

    def test_processors(self):
        self.extractor(tables, processors=[simple_processor])
        self.assertTrue(len(self.extractor) > 0)

    def test_can_get_item(self):
        pass

    def test_can_iter(self):
        for value in self.extractor:
            self.assertIsInstance(value, list)


if __name__ == "__main__":
    unittest.main()
    
    # runner = unittest.TextTestRunner()
    # suite = unittest.TestSuite()
    # suite.addTest(TestRowsExtractor('test_using_soup'))
    # runner.run(suite)
