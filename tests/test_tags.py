import unittest

from bs4 import BeautifulSoup
from bs4.element import Tag
from zineb.extractors.base import TableExtractor
from zineb.tags import Link, TableTag

path = 'tests/html/test_links.html'
with open(path, mode='r') as f:
    soup = BeautifulSoup(f, 'html.parser')
    links = soup.find_all('a')
    link = links[-1]


class TestLinkTag(unittest.TestCase):
    def setUp(self):
        self.link = Link(link, attrs=link.attrs)

    def test_has_tag(self):
        self.assertIsNotNone(self.link.tag)
        self.assertIsInstance(self.link.tag, Tag)

    def test_contains(self):
        self.assertTrue('gmail' in self.link)
        self.assertTrue('kendall' in self.link)


path = 'tests/html/tables.html'
with open(path, mode='r') as f:
    soup = BeautifulSoup(f, 'html.parser')
    table = soup.find('table')


class TestTableTag(unittest.TestCase):
    def setUp(self):
        self.table = TableTag(table, soup)

    def test_resolution(self):
        self.assertIsInstance(self.table.rows, list)
        extractor, rows = self.table.data()
        self.assertIsInstance(rows, list) 
        self.assertIsInstance(extractor, TableExtractor)


if __name__ == "__main__":
    unittest.main()
