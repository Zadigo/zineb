import unittest
from zineb.html_parser.html_tags import Tag, ElementData
from zineb.html_parser.utils import filter_by_attrs, filter_by_name, filter_by_name_or_attrs

link = Tag('a', attrs=[('id', 'test')])
span = Tag('span')
span_data = ElementData('Question')
div = Tag('div')

link._children = [span, span_data]
span._internal_data = [span_data]

tags = [link, span, span_data, div]

class TestFilters(unittest.TestCase):
    def test_filter_by_name(self):
        result = filter_by_name(tags, 'span')
        for item in result:
            with self.subTest(item=item):
                self.assertEqual(item.name, 'span')
                
    def test_filter_by_attrs(self):
        result = filter_by_attrs(tags, {'id': 'test'})
        for item in result:
            with self.subTest(item=item):
                self.assertEqual(item.name, 'a')
    
    def test_filter_by_name_and_attrs(self):
        result = filter_by_name_or_attrs(tags, 'a', {'id': 'test'})
        for item in result:
            with self.subTest(item=item):
                self.assertEqual(item.name, 'a')
        
                        
if __name__ == '__main__':
    unittest.main()
