from functools import cached_property
from typing import Iterator

from zineb.html_parser.builders import BaseBuilder

class Queryset:
    def __init__(self, tags: list):
        self.tags = tags
        self.count = 0

    def __repr__(self):
        return f"{self.__class__.__name__}({self.tags})"
    
    @classmethod
    def copy(cls, tags: Iterator):
        tags = list(tags)
        instance = cls(tags)
        instance.count = len(tags)
        return instance


class Soup:
    def __init__(self, html_text: str):
        builder = BaseBuilder()
        builder.start_iteration(html_text)
        self.builer = builder
        self.builer.finalize()

    def __repr__(self):
        return str(self.builer.html_tree)

    @property
    def html_tree(self):
        return self.builer.html_tree

    # def _iterate_over_tree(self, name, attrs={}):

    def _get_opening_closing_tags(self, name):
        matched_index = None
        matched_closing_index = None
        for i, tag in enumerate(self.html_tree):
            if matched_index is None:
                if tag == name:
                    matched_index = i

            if matched_closing_index is None:
                if tag == name and tag.is_closing_tag:
                    matched_closing_index = i
        return matched_index, matched_closing_index
        # return self.html_tree[matched_index:matched_closing_index]

    def find(self, name: str, attrs: dict={}):
        queryset = self._get_opening_closing_tags(name)
        print(queryset)
    
    def find_all(self, name: str, attrs: dict={}):
        # queryset = self._iterate_over_tree(name, attrs=attrs)
        # return Queryset.copy(queryset)
        pass
