import unittest

from zineb.html_parser.parsers import Extractor
from zineb.tests.html_parser import items


class TestExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = Extractor()

    def test_resolution_of_normal_html(self):
        self.extractor.resolve(items.NORMAL_HTML)
        self.assertGreater(len(self.extractor), 0)
        
    def test_tag_creation_functions(self):
        self.extractor.start_tag('a', [('id', 'test')])
        link = self.extractor.container_as_queryset.first
        self.assertIn(link, self.extractor)
        
        # The created tag should technically not
        # be closed since we did not call end_tag
        self.assertFalse(self.extractor.container[0].closed)
        
        self.extractor.end_tag('a')
        self.assertTrue(self.extractor.container[0].closed)
        
    def test_complex_tag_creation(self):
        virtual_tree = ['html', 'body', 'a']
        for i, item in enumerate(virtual_tree):
            self.extractor.start_tag(item, [], position=(None, None), index=i)
            
        for item in virtual_tree:
            self.extractor.end_tag(item)
        
        self.assertEqual(len(self.extractor), 3)
        
        # Technically, <body> should be child of
        # <html> and <a> of html
        html = self.extractor.container[0]
        body = self.extractor.container[1]

        self.assertEqual(len(html._children), 2)
        self.assertEqual(len(body._children), 1)
        
        
if __name__ == '__main__':
    unittest.main()
