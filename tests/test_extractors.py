import unittest

import pandas
from bs4 import BeautifulSoup
from zineb.extractors.base import ImageExtractor, LinkExtractor, TableRows
from zineb.tags import ImageTag

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
    extractor_class = ImageExtractor

    def test_image_extraction(self):
        extractor = self.extractor_class()
        images = extractor.resolve(soup)
        self.assertGreater(len(images), 0)
        image = images[0]
        self.assertIsInstance(image, ImageTag)

    def test_filtering(self):
        extractor = self.extractor_class(url_must_contain='Ambrosio')
        images = extractor.resolve(soup)

        filtered_images = extractor.filter_images()
        self.assertNotEqual(len(images), len(filtered_images))

        filtered_images = extractor.filter_images('901')
        self.assertIn('Alessandra-Ambrosio-Booty-in-Bikini-901.jpg', filtered_images[0])


class TestRowsExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = TableRows(has_headers=True)

    def test_resolution(self):
        result = self.extractor.resolve(soup2)
        self.assertIsInstance(result, list)

    def test_using_specific_table(self):
        rows = self.extractor.resolve(tables[10])
        self.assertIsInstance(rows, list)
        self.assertIsInstance(rows[-1], list)
        self.assertIn('Erika', rows[2])

    def test_processors(self):
        def replace_empty_values(value, row=None):
            if value is None or value == '':
                return None
            else:
                return value

        extractor = TableRows(has_headers=True, processors=[replace_empty_values])
        rows = extractor.resolve(player_table)
        self.assertNotIn('', rows[2])

    def test_pandas_resolution(self):
        extractor = TableRows(has_headers=True)
        df = extractor.resolve_to_dataframe()
        self.assertIsInstance(df, pandas.DataFrame)
        print(extractor._compose)

if __name__ == "__main__":
    unittest.main()
    
    # runner = unittest.TextTestRunner()
    # suite = unittest.TestSuite()
    # suite.addTest(TestRowsExtractor('test_using_soup'))
    # runner.run(suite)
