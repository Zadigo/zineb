from functools import cached_property
from typing import Union

from zineb.html_parser.html_tags import Tag
from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.utils import HTML_TAGS
from zineb.utils.iteration import keep_while


class Manager:
    def __init__(self, instance):
        self.instance = instance

    def __getattr__(self, value):
        if value in HTML_TAGS:
            return self.find(value)
        return value

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @cached_property
    def get_title(self) -> str:
        title = None
        with self.instance as items:
            for item in items:
                if item.name == 'title':
                    title = item.string
                    break
        return title

    @cached_property
    def links(self):
        """Returns all the links contained in the HTML page"""
        return self.find_all('a')

    @cached_property
    def tables(self):
        """Returns all the tables contained within the HTML page"""
        return self.find_all('table')

    def find(self, name: str, attrs: dict = {}) -> Tag:
        """Returns the first found element"""
        tag_to_return = None
        for tag in self.instance.get_container:
            if tag == name:
                if attrs:
                    for attr, value in attrs.items():
                        result = tag.get_attr(attr)
                        if result is not None:
                            if result == value and tag == name:
                                tag_to_return = tag
                else:
                    tag_to_return = tag
                    break
        return tag_to_return

    def find_all(self, name_or_names: Union[str, list], attrs: dict = None):
        """Finds all the elements"""
        def filtering_function(tag):
            if isinstance(name_or_names, list):
                return tag.name in name_or_names
            return tag == name_or_names

        queryset = keep_while(filtering_function, self.instance.get_container)
        return QuerySet.copy(queryset)

    # def filter(self, **expressions):
    #     """A function that allows finding items using query expressions"""
    #     tokens = []
    #     for key, value in expressions.items():
    #         # a__class__eq="google"
    #         items = key.split('__')
    #         if len(items) < 2:
    #             raise ValueError(
    #                 'Expression should contain at least 2 values: the tag name and the attribute e.g. a__class')
    #         if len(items) == 2:
    #             items.append('eq')

    #         tokens.append((items, value))

    #     tags = []
    #     for lhs, rhs in tokens:
    #         name, attr, comparator = lhs
    #         tag = self.find(name, attrs={attr: rhs})
    #         tags.append(tag)
    #     return QuerySet.copy(tags)

    def save(self, filename: str):
        pass

    def live_update(self, url: str=None, html: str=None):
        """Fetch a newer version of the html page
        using a url or a string"""
