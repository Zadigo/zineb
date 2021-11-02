from collections import deque
from functools import cached_property

from zineb.html_parser.algorithm import CustomHTMLParser
from zineb.html_parser.tags import ClosingTag, Comment, SimpleData, Tag
from zineb.html_parser.utils import requires_closing


class BaseBuilder:
    """This is the main class that converts the HTML data
    parsed from the parser into a python object"""

    parser = CustomHTMLParser

    TREE = deque()

    def __init__(self):
        # self.top_parent = None
        self._last_tag = None

        self._html_body = None
        self._current_tag = None
        self._current_data_tag = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.html_tree})"

    @classmethod
    def start_iteration(cls, html_text: str):
        builder_instance = cls()
        parser = builder_instance.parser(builder_instance)
        parser.feed(html_text)
        parser.close()

    @property
    def html_tree(self):
        return list(self.TREE)

    @property
    def _get_last_item(self):
        return self.TREE[-1]

    @cached_property
    def number_of_tags(self):
        return len(self.html_tree)

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

    # def _add_child_to_current(self, tag):
    #     # Adds an element to the current tag
    #     # this is tracked
    #     if self._current_tag is not None and not self._current_tag.is_data:
    #         self._current_tag.add_child(tag)

    # def _add_child_to_previous(self, tag):
    #     current_number_of_items = len(self.TREE)
    #     previous_tag = self.TREE[current_number_of_items]
    #     if not previous_tag.is_data:
    #         previous_tag.add_child(tag)

    # def _add_child_to_previous_tags(self, tag):
    #     # Backward add the current tag
    #     # to all the tags integrated before
    #     # the current tag is appended
    #     current_number_of_items = len(self.TREE)
    #     for i in range(current_number_of_items, 0, -1):
    #         previous_tag = self.TREE[i - 1]
    #         if not previous_tag.is_data:
    #             previous_tag.add_child(tag)

    def handle_inner_data(self, data: str):
        tag = SimpleData(data)

        self._current_data_tag = tag
        self.add_to_tree(tag)

    def handle_start_tag(self, name: str, attrs: dict, **kwargs):
        tag = Tag.as_instance(name=name, attrs=attrs, self_closing=False)

        self._current_tag = tag
        self.add_to_tree(tag)

    def handle_end_tag(self, name: str):
        if self._last_tag is not None:
            if self._last_tag.name == name:
                pass

        if requires_closing(name):
            closing_tag = ClosingTag(name)
            self.add_to_tree(closing_tag)

    def handle_comment(self, data: str):
        tag = Comment(data)
        self.add_to_tree(tag)

    def handle_self_closing_tag(self, name: str, attrs: list):
        tag = Tag(name, attrs, self_closing=True)
        self.add_to_tree(tag)
