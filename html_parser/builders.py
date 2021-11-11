from collections import deque
from functools import cached_property
from typing import Callable, Counter

from zineb.html_parser.algorithm import CustomHTMLParser
from zineb.html_parser.tags import (ClosingTag, Comment, HTMLDocument, SimpleData,
                                    Tag)
from zineb.html_parser.utils import SELF_CLOSING_TAGS, requires_closing


class BaseBuilder:
    """This is the main class that converts the HTML data
    parsed from the parser into a python object"""

    parser = CustomHTMLParser

    TREE = deque()

    def __init__(self):
        # self.parent = HTMLDocument.as_instance()
        # self._html_body = None
        self._current_tag = None
        self._current_data = []
        self._unclosed_tags = Counter()
        self._collected_tags = []

    def __repr__(self):
        return f"{self.__class__.__name__}({self.html_tree})"
        # return f"{self.__class__.__name__}({self.parent})"
    
    @classmethod
    def start_iteration(cls, html_text: str, document: Callable=None):
        builder_instance = cls()
        parser = builder_instance.parser(builder_instance)
        # builder.TREE.append()
        parser.feed(html_text)
        parser.close()

    @property
    def html_tree(self):
        return list(self.TREE)

    @property
    def _get_last_item(self):
        try:
            return self.TREE[-1]
        except:
            return None
    
    @cached_property
    def number_of_tags(self):
        return len(self.html_tree)
    
    def is_self_closing(self, name):
        return name in SELF_CLOSING_TAGS

    def finalize(self, stop_on_first_match=False):
        """Iterates over the whole tree once each
        element was parsed to establish relationships
        between items and create the final relevant
        tree structure"""

        number_of_items = len(self.TREE)
        # previous_tag = None
        for i, tag in enumerate(self.TREE):
            next_index = i + 1

            if i > 0:
                setattr(tag, 'previous_element', self.TREE[i - 1])
                # We'll only keep track of opening
                # tags since for siblings we do not
                # need to know about the closing ones
                if not tag.is_closing_tag:
                    previous_tag = self.TREE[i - 1]

            if next_index < number_of_items:
                setattr(tag, 'next_element', self.TREE[next_index])

            # if not tag.is_closing_tag:
            #     if getattr(tag, 'next_sibling') is None:
            #         if previous_tag is not None:
            #             if tag.name == previous_tag.name:
            #                 setattr(tag, 'next_sibling', None)

    def add_to_tree(self, tag):
        self.TREE.append(tag)
        
    def handle_inner_data(self, data: str):
        tag = SimpleData(data)

        self.add_to_tree(tag)
        self._current_data.append(tag)
        
        # We had a previous tag, also implement
        # it in the current tag
        if self._current_tag is not None and not self._current_tag.is_data:
            self._current_tag.add_child(tag)
        # self.parent.add_child(tag)

    def handle_start_tag(self, name: str, attrs: dict, **kwargs):
        tag = Tag.as_instance(name=name, attrs=attrs, self_closing=False)
        tag.self_closing = self.is_self_closing(name)
        
        # Track the tags that are currently opened
        # and close them when they are met in the
        # handle_end_tag definition
        self._unclosed_tags.update(name)

        # If we have data that was parsed, integrate
        # it in the current tag
        # if self._current_data_tag is not None:
        #     self._current_tag.add_child(tag)

        # We had a previous tag, also implement
        # it in the current tag
        if self._current_tag is not None:
            self._current_tag.add_child(tag)
        
        # self.parent.add_child(tag)
        self.add_to_tree(tag)
        self._current_tag = self._get_last_item

    def handle_end_tag(self, name: str, nsprefix=None):
        self._unclosed_tags.subtract(name)
        if self._get_last_item is not None:
            self._get_last_item.closed = True
            
        # if self._current_data:
            
        # if requires_closing(name):
        #     closing_tag = ClosingTag(name)
        #     self.add_to_tree(closing_tag)
            
        # self._current_data = None

    def handle_comment(self, data: str):
        tag = Comment(data)
        self.add_to_tree(tag)

    def handle_self_closing_tag(self, name: str, attrs: list):
        tag = Tag(name, attrs, self_closing=True)
        self.add_to_tree(tag)
        # We assume that when a tag is closed,
        # then the current data that was collected
        # is part of that tag and therefore should
        # be reset
        self._current_data = []
        
HTML = """<html>Simple</html>"""
# HTML = """<html><div></div><div></div></html>"""
builder = BaseBuilder()
builder.start_iteration(HTML)
print(builder)
