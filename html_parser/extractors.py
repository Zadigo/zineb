from enum import unique
from functools import cached_property
from typing import List

from zineb.html_parser.html_tags import Tag
from zineb.html_parser.parsers import Extractor
from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.utils import break_when
from zineb.utils.iteration import keep_while

TABLE_TAGS = ['table', 'thead', 'tr', 'th', 'td', 'tbody']


class TableExtractor(Extractor):
    def __init__(self, class_or_id_name: str=None, base_url: str=None, processors: List=[]):
        super().__init__()
        self.class_or_id_name = class_or_id_name
        self.base_url = base_url
        self.processors = set(processors)
    
    @cached_property
    def get_rows(self):
        table_body = break_when(lambda x: x == 'tbody', self.container)
        return table_body.find_all('tr')
    
    @cached_property
    def extract_values(self):
        rows = []
        for row in self.get_rows:
            columns = row.find_all('td')
            column_to_add = []
            for column in columns:
                column_to_add.extend([column.string])
            rows.append(column_to_add)
        return rows

    @property
    def first(self):
        return self.get_row(0)
    
    def get_row(self, index: int):
        return self.get_rows[index]
    
    def start_tag(self, tag, attrs, **kwargs):
        if tag in TABLE_TAGS:
            instance = Tag(tag, attrs, extractor=self)
            self.container.append(instance)
            self._current_tag = instance
            
            self.recursively_add_tag(instance)
            
    def end_tag(self, tag):
        def filtering_function(x):
            return x == 'table' and not x.closed
        tag_to_close = break_when(filtering_function, self.container)
        tag_to_close.closed = True
        
    def self_closing_tag(self, tag, attrs, **kwargs):
        return False
        
    def parse_comment(self, data: str, **kwargs):
        return False
    

class TextExtractor(Extractor):
    """An extractor that can get all the text from
    a given html page"""
    def start_tag(self, tag, attrs, **kwargs):
        return False
    
    def end_tag(self, tag):
        return False
    
    def self_closing_tag(self, tag, attrs, **kwargs):
        return False
    
    
class ImageExtractor(Extractor):
    """An extractor that returns all the images present
    on the given html page"""
    
    def __init__(self, unique: bool=False, as_type: str=None,
                 url_must_contain: str=None, match_height: int=None,
                 match_width: int=None):
        super().__init__()
        self.unique = unique
        self.as_type = as_type
        self.url_must_contain = url_must_contain
        self.match_height = match_height
        self.match_width = match_width
        self.processors = []
        
        # Checks whether an url was already
        # processed by the extractor
        self._processed_urls = set()
        
    def _run_processors(self):
        pass
        
    def get_images(self):
        filtered_images = []
        
        if self.unique:
            urls = set()
            for image in self.container:
                if image['src'] not in urls:
                    urls.add(image['src'])
                    filtered_images.append(image)
                    
        if self.as_type is not None:
            images = filtered_images or self.container
            filtered_images = keep_while(lambda x: x['src'].endswith(self.as_type), images)
            
        if self.url_must_contain is not None:
            images = filtered_images or self.container
            filtered_images = keep_while(lambda x: self.url_must_contain in x['src'], images)

        return QuerySet.copy(filtered_images or self.container)
    
    def download_images(self):
        pass
        
    def start_tag(self, tag, attrs, **kwargs):
        return False
            
    def end_tag(self, tag):
        return False
    
    def internal_data(self, data):
        return False
        
    def parse_comment(self, data: str, **kwargs):
        return False
        
    def self_closing_tag(self, tag, attrs, **kwargs):
        self._opened_tags.update([tag])
        
        klass = Tag(tag, attrs, extractor=self)
        self.container.append(klass)
        self._current_tag = klass
        klass.closed = True
