import unittest
from zineb.html_parser.html_tags import Tag, ElementData
from zineb.html_parser.utils import filter_by_attrs, filter_by_name, filter_by_name_or_attrs

# div + a > span{Question}
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
                
    def test_filter_by_name_not_exist(self):
        result = filter_by_name(tags, 'p')
        self.assertListEqual(list(result), [])
                
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
                self.assertDictEqual(item.attrs, {'id': 'test'})
    
    def test_filter_imbrication(self):
        by_names = filter_by_name(tags, 'a')
        by_attrs = filter_by_attrs(by_names, {'id': 'test'})
        self.assertEqual(len(list(by_attrs)), 1)
        
                        
if __name__ == '__main__':
    unittest.main()
