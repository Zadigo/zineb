import secrets
from functools import cached_property
from typing import Union

from zineb.html_parser.html_tags import BaseTag, Tag
from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.utils import (HTML_TAGS, SELF_CLOSING_TAGS,
                                     filter_by_name_or_attrs)

from html_parser.utils import filter_by_name


class Manager:
    def __init__(self, extractor):
        self._extractor_instance = extractor

    # def __getattr__(self, value):
    #     # Allows something like x.manager.div
    #     # which will return the first
    #     # matching item in the collection
    #     if value in HTML_TAGS:
    #         return self.find(value)
    #     return value

    def __repr__(self):
        name = f"{self._extractor_instance.__class__.__name__}{self.__class__.__name__}"
        return f"{name}(tags={len(self._extractor_instance)})"

    @cached_property
    def get_title(self) -> Union[str, None]:
        items = filter_by_name(self._extractor_instance, 'title')
        try:
            return list(items)[0]
        except:
            return None

    # @cached_property
    # def links(self):
    #     """Returns all the links contained 
    #     in the HTML page"""
    #     return self.find_all('a')

    # @cached_property
    # def tables(self):
    #     """Returns all the tables contained 
    #     within the HTML page"""
    #     return self.find_all('table')

    def find(self, name: str, attrs: dict = {}) -> Tag:
        """Get a tag by name or attribute. If there are multiple
        tags, the first item of the list is returned"""
        result = filter_by_name_or_attrs(self._extractor_instance, name, attrs)
        try:
            return list(result)[0]
        except IndexError:
            raise ValueError('Tag with x does not exist')

    def find_all(self, name: Union[str, list], attrs: dict = None):
        """Filter tags by name or by attributes"""
        result = filter_by_name_or_attrs(self._extractor_instance, name, attrs)
        return QuerySet.copy(result)
    
    # def download_images(self, func: Callable):
    #     """Download all the images on the page using
    #     a function that should send a request and return
    #     the image's content as bytes"""
    #     if not callable(func):
    #         raise TypeError('Function should be a callable')
        
    #     image_types = ['jpg', 'jpeg', 'png', 'svg']
        
    #     images = self.find_all('a')
    #     for image in images:
    #         url = image.get_attr('src')
    #         try:
    #             content = func(url)
    #         except:
    #             yield False
    #         else:
    #             if not isinstance(content, bytes):
    #                 raise ValueError('Image content should be bytes')
                
    #             from PIL import Image
    #             instance = Image.open(content)
                
    #             _, extension = url.split('.')
    #             name = f"{secrets.token_hex(n=5)}.{extension}"
    #             with open(name, mode='wb') as f:
    #                 instance.save(f)
    #                 yield True

    # def save(self, filename: str):
    #     pass

    # def live_update(self, url: str=None, html: str=None):
    #     """Fetch a newer version of the html page
    #     using a url or a string"""

    # def insert(self, position: int, tag: Callable):
    #     """Insert a tag at the designed position
    #     within the global collection"""
    #     if not self._has_extractor:
    #         raise TypeError('To use to query with tags, need an extractor')

    #     if not isinstance(tag, BaseTag):
    #         raise TypeError('Tag should be an instance of BaseTag')

    #     self._extractor_instance.container.insert(position, tag)
        
    # def to_representation(self):
    #     html_tree = []
    #     items = self._create_representation()
    #     current_unclosed = None
    #     for item in items:
    #         if item == '\n':
    #             html_tree.append(item)
    #         else:
    #             matched = re.match(r'^\<(\w+)')
    #             if matched:
    #                 if matched.group(1) not in SELF_CLOSING_TAGS:
    #                     current_unclosed = item
    #             else:
    #                 html_tree.append(item)
                    
    #     # from lxml.etree import fromstring
    #     # from lxml.html import tostring
    #     # html = fromstring(html)
    #     # return tostring(html, pretty_print=True, encoding='utf-8')
            
    # def _create_representation(self):
    #     """Show the actual representation of
    #     the Python collection of tags"""
    #     html_tree = []
    #     with self._extractor_instance as tags:
    #         for tag in tags:
    #             if tag.name == 'newline':
    #                 yield '\n'
    #             elif tag.name == 'data':
    #                 yield tag.data
    #             else:
    #                 template = '<{name} {attrs}>'
    #                 yield template.format(name=tag.name, attrs=tag._attrs_to_string)
    #     return html_tree
