from typing import Callable

from zineb.html_parser.utils import is_empty, is_newline

START_TAG = '<'

END_TAG = '/>'

TAG_TEMPLATE = '<{tag}>{content}<{tag}/>'

TAG_WITH_ATTRS_TEMPLATE = '<{tag} {attrs}>{content}<{tag}/>'

SELF_CLOSING_TEMPLATE = '<{tag} {attrs}/>'

COMMENT_TEMPLATE = '<!-- {content} -->'


def attrs_to_text(attrs: dict):
    results = []
    for key, values in attrs.items():
        name = key
        items = ''

        if not isinstance(values, list):
            values = [values]

        for i, value in enumerate(values):
            if i > 0:
                value = f' {value}'
            items = items + f'{value}'
        results.append(f'{name}="{items}"')
    return ' '.join(results)


def create_representation(tag: str, content: str, self_closing: bool=False, attrs: dict={}, **kwargs):
    """Visually represents a python tag to its true
    HTML value"""
    attrs = attrs_to_text(attrs)
    kwargs.update(tag=tag, content=content, attrs=attrs)

    if self_closing:
        return SELF_CLOSING_TEMPLATE.format(**kwargs)

    if attrs:
        return TAG_WITH_ATTRS_TEMPLATE.format(**kwargs)
    return TAG_TEMPLATE.format(**kwargs)


class NavigationMixin:
    def __init__(self, top_parent=None):
        self.top_parent = top_parent
        self.parent = None
        self.previous_element = None
        self.next_element = None
        self.next_sibling = None
        self.previous_sibling = None

    @property
    def is_closing_tag(self):
        return self.category == 'closing'

    @property
    def is_data(self):
        special_tags = ['data', 'comment']
        return self.category in special_tags


class BaseTag(NavigationMixin):
    category = None

    def __init__(self, name: str, attrs: dict, self_closing: bool=False, **kwargs):
        self.name = name
        self.attrs = attrs
        self.self_closing = self_closing
        self.closed = False
        # Contains all the children elements
        # that are contained within a given tag
        self.contents = []
        super().__init__(top_parent=kwargs.get('top_parent', None))

    def __repr__(self):
        return self.name
        # return create_representation(self.name, None, self_closing=self.self_closing, attrs=self.attrs)

    def __eq__(self, name):
        return self.name == name

    @classmethod
    def as_instance(cls, **kwargs):
        instance = cls(**kwargs)
        return instance

    # @cached_property
    # def previous_sibling(self):
    #     pass
    
    # @cached_property
    # def next_sibling(self):
    #     pass

    # @cached_property
    # def previous_element(self):
    #     pass

    # @cached_property
    # def next_element(self):
    #     pass

    def add_child(self, tag: Callable):
        self.contents.append(tag)

    def has_attr(self, name: str):
        return name in self.attrs


class Tag(BaseTag):
    category = 'tag'
      

class SimpleData(NavigationMixin):
    category = 'data'

    def __init__(self, value: str):
        self.text = value
        self.is_empty = is_empty(value)
        self.is_newline = is_newline(value)
        super().__init__()

    def __repr__(self):
        if self.is_empty:
            return 'empty'

        if self.is_newline:
            return 'newline'
        
        return self.text

    def __eq__(self, text):
        return self.text == text

    @property
    def is_empty_or_newline(self):
        return self.is_empty or self.is_newline


class Comment(SimpleData):
    category = 'comment'

    def __repr__(self):
        return self.text


class ClosingTag(NavigationMixin):
    """This dummy function serves as an only purpose to mark
    the that a given tag should be closed"""

    category = 'closing'

    def __init__(self, name):
        self.name = name
        super().__init__()

    def __repr__(self):
        return f'<--{self.name}-->'
