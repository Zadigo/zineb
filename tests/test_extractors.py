import unittest

from bs4 import BeautifulSoup
from zineb.extractors.images import ImageExtractor
from zineb.extractors.base import TableRows
from zineb.extractors.links import LinkExtractor
from zineb.dom.tags import ImageTag



with open('tests/html/images.html', 'r') as f:
    soup = BeautifulSoup(f, 'html.parser')


with open('tests/html/tables2.html', 'r') as f:
    soup2 = BeautifulSoup(f, 'html.parser')
    tables = soup2.find_all('table')
    player_table = None
    for table in tables:
        if table.has_attr('width'):
            width = table.attrs.get('width')
            if width == '631':
                player_table = table
    

class TestImagesExtractor(unittest.TestCase):
    def test_image_extraction(self):
        extractor = ImageExtractor()
        images = extractor.resolve(soup)
        self.assertGreater(len(images), 0)
        image = images[0]
        self.assertIsInstance(image, ImageTag)

    def test_filtering(self):
        extractor = ImageExtractor(url_must_contain='Ambrosio')
        images = extractor.resolve(soup)

        filtered_images = extractor.filter_images()
        self.assertNotEqual(len(images), len(filtered_images))

        filtered_images = extractor.filter_images('901')
        # self.assertIn(filtered_images, 'Alessandra-Ambrosio-Booty-in-Bikini-901.jpg')

    def test_image_downloading(self):
        pass


class TestRowsExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = TableRows(has_headers=True)

    def test_using_soup(self):
        self.extractor.resolve(soup)

    def test_using_specific_table(self):
        rows = self.extractor.resolve(tables[10])
        self.assertIsInstance(rows, list)
        self.assertIsInstance(rows[-1], list)
        self.assertIn('Erika', rows[2])

    def test_processors(self):
        def drop_empty_values(value):
            if value is not None or value != '':
                return value

        extractor = TableRows(has_headers=True, processors=[drop_empty_values])
        rows = extractor.resolve(soup)
        self.assertNotIn('', rows[2])


def clean_values(value, **kwargs):
    if value != '' or value is not None:
        return value


# if __name__ == "__main__":
#     unittest.main()
    
    # runner = unittest.TextTestRunner()
    # suite = unittest.TestSuite()
    # suite.addTest(TestRowsExtractor('test_using_soup'))
    # runner.run(suite)
