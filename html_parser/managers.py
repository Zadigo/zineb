from functools import cached_property
from typing import Union

from zineb.html_parser.html_tags import Tag
from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.utils import HTML_TAGS, filter_by_name_or_attrs


class Manager:
    def __init__(self, extractor):
        self._extractor_instance = extractor

    def __getattr__(self, value):
        if value in HTML_TAGS:
            return self.find(value)
        return value

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @cached_property
    def get_title(self) -> str:
        title = None
        with self._extractor_instance as items:
            for item in items:
                if item.name == 'title':
                    title = item.string
                    break
        return title

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

    def save(self, filename: str):
        pass

    def live_update(self, url: str=None, html: str=None):
        """Fetch a newer version of the html page
        using a url or a string"""
