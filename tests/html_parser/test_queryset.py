import unittest

from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.html_tags import ElementData, Tag


class TestQueryset(unittest.TestCase):
    def setUp(self):
        # <html><body><span>Something</span></body></html>
        html = Tag('html')
        body = Tag('body')
        span = Tag('span')
        
        span_data = ElementData('Something')
        span._internal_data = [span_data]
        
        html._children = [body, span, span_data]
        body._children = [span, span_data]
        
        container = [html, body, span, span_data]
        
        self.queryset = QuerySet.copy(container)
        
    def test_exists(self):
        self.assertTrue(self.queryset.exists())
        
    def test_count(self):
        self.assertEqual(self.queryset.count, 4)
        
    def test_first(self):
        self.assertEqual(self.queryset.first.name, 'html')
        
    def test_last(self):
        self.assertEqual(self.queryset.last.name, 'data')
        
    def test_find_all(self):
        result = self.queryset.find_all('span')
        for item in result:
            with self.subTest(item=item):
                self.assertTrue(item.name == 'span')
                
    def test_exclude(self):
        result = self.queryset.exclude('span')
        for item in result:
            with self.subTest(item=item):
                self.assertTrue(item.name != 'span')
                
    def test_distinct(self):
        pass
    
    def test_values(self):
        pass
    
    def test_dates(self):
        pass
    
    def test_union(self):
        pass
    
    def test_contains(self):
        result = self.queryset.contains('span')
        self.assertTrue(result)
        
        result = self.queryset.contains('a')
        self.assertFalse(result)
    
    def test_explain(self): 
        pass
    
    def test_generator(self): 
        pass
                

if __name__ == '__main__':
    unittest.main()
