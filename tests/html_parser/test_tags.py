import unittest

from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.tags import BaseTag, ElementData, NewLine, Tag

# TAGS = [Tag('a'), Tag('a', attrs=[('id', 'test')]), Tag('p', attrs=[('data-test', 'test')])]

class TestBaseTag(unittest.TestCase):
    def test_has_attribute(self):
        tag = Tag('a')
        self.assertFalse(tag.has_attr('id'))
        
    def test_build_attrs(self):
        tag = Tag('a')
        tag.attrs = tag._build_attrs([('id', 'test')])
        self.assertDictEqual(tag.attrs, {'id': 'test'})
        
    def test_attrs_to_string(self):
        # Test that we get the correct formating
        # when converting the dict attrs to string
        # attrs
        tag = Tag('a', attrs=[('id', 'test')])
        self.assertEqual(tag._attrs_to_string, 'id="test"')
        
    def test_find(self):
        # <a><span>something</span></a>
        link = Tag('a')
    
        span = Tag('span')
        span._internal_data = [ElementData('something')]
        
        link._children = [span]
        
        result = link.find('span')
        self.assertIsInstance(result, BaseTag)
        self.assertEqual(result.string, 'something')
        
    def test_find_all(self):
        # <a><span>1</span><p>2</p></a>
        link = Tag('a')

        span1 = Tag('span')
        span1._internal_data = [ElementData('1')]
        span2 = Tag('span')
        span2._internal_data = [ElementData('2')]
        
        link._children = [span1, span2]
        
        result = link.find_all('span')
        self.assertIsInstance(result, QuerySet)
        
        first_span = result.first
        self.assertEqual(first_span.string, '1')
            
    def test_can_get_string(self):
        # Test that we can get the string contained
        # within the tag when we call the property
        tag = Tag('a')
        tag._internal_data = [ElementData('something')]
        self.assertEqual(tag.string, 'something')
        
        # Test that when we have multiple tags within
        # the given tag, that we get None
        tag._internal_data = [ElementData('something'), NewLine()]
        self.assertIsNone(tag.string)
    
    
if __name__ == '__main__':
    unittest.main()
