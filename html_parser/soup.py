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

    @cached_property
    def html_tree(self):
        return self.builer.html_tree

    def _iterate_over_tree(self, name, attrs={}):
        # Internal function used to iterate
        # over the html tree
        for tag in self.html_tree:
            if tag == name:
                yield tag

    def find(self, name: str, attrs: dict={}):
        pass
    
    def find_all(self, name: str, attrs: dict={}):
        queryset = self._iterate_over_tree(name, attrs=attrs)
        return Queryset.copy(queryset)
