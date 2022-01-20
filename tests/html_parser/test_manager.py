import unittest

from zineb.html_parser.html_tags import ElementData
from zineb.html_parser.managers import Manager
from zineb.html_parser.parsers import Extractor
from zineb.html_parser.queryset import QuerySet
from zineb.tests.html_parser import items


class TestManager(unittest.TestCase):
    def setUp(self):
        extractor = Extractor()
        extractor.resolve(items.NORMAL_HTML)
        self.manager = Manager(extractor)

    def test_find(self):
        tag = self.manager.find('a')
        self.assertEqual(tag.name, 'a')
        self.assertEqual(tag.string, 'Question')
        
    def test_find_all(self):
        tags = self.manager.find_all('a')
        self.assertEqual(len(tags), 3)
        self.assertIsInstance(tags, QuerySet)
        
        # Assert that each tag that we got
        # are links and not anything else
        
        for item in tags:
            with self.subTest(item=item):
                self.assertEqual(item.name, 'a')
                
    def test_find_all_with_attrs(self):
        # TODO:
        tags = self.manager.find_all('a', attrs={'id': 'test'})
        
        self.assertEqual(len(tags), 1)
        self.assertIsInstance(tags, QuerySet)

        # Assert that each tag that we got
        # are links and not anything else

        for item in tags:
            with self.subTest(item=item):
                self.assertEqual(item.name, 'a')
                
    def test_links_property(self):
        pass
        # print(self.manager.links)
        # self.assertIsInstance(self.manager.links, QuerySet)
        
        # for item in self.manager.links:
        #     with self.subTest(item=item):
        #         # self.assertEqual(item.name, 'a')
        #         self.assertIsInstance(item)
    
    # def test_string(self):
    #     tag = self.manager.find('a')
    #     self.assertTrue(isinstance(tag.string, ElementData))
    #     self.assertIsInstance(tag.string, 'Question')
        
if __name__ == '__main__':
    unittest.main()
