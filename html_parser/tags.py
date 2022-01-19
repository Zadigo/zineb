from collections import OrderedDict, deque
from typing import Callable, Union

from zineb.html_parser.queryset import QuerySet
from zineb.utils.characters import deep_clean


class QueryMixin:
    @property
    def _has_extractor(self):
        return self._extractor_instance is not None

    @property
    def previous_element(self):
        """Return the element directly before this tag"""
        pass

    @property
    def next_element(self):
        """Return the element directly next to this tag"""
        position_of_next = self.vertical_position + 1
        for item in self._extractor_instance.get_container:
            if item.vertical_position == position_of_next:
                break
        return item

    @property
    def contents(self):
        return QuerySet.copy(self._internal_data)

    def get_attr(self, name: str) -> Union[str, None]:
        return self.attrs.get(name, None)

    def get_previous(self, name: str):
        with self._extractor_instance as items:
            pass

    def get_next(self, name: str):
        with self._extractor_instance as items:
            pass

    def get_all_previous(self, name: str):
        if not self._has_extractor:
            raise TypeError('To use to query with tags, need an extractor')
            # return []

        def filtering_function():
            with self._extractor_instance as items:
                for item in items:
                    if (item.vertical_position < self.vertical_position and
                            item.name == name):
                        yield item

        return QuerySet.copy(filtering_function())

    def get_all_next(self, name: str):
        if not self._has_extractor:
            raise TypeError('To use to query with tags, need an extractor')

        def filtering_function():
            with self._extractor_instance as items:
                for item in items:
                    if (item.vertical_position > self.vertical_position and
                            item.name == name):
                        yield item

        return QuerySet.copy(filtering_function())

    def children(self, **expression):
        pass

    def get_parent(self, name: str):
        pass

    def get_previous_sibling(self, name: str):
        pass

    def get_next_sibling(self, name: str):
        pass


class BaseTag(QueryMixin):
    def __init__(self, name: str, attrs: dict = {}, extractor: Callable = None):
        self.name = name
        self.attrs = self._build_attrs(attrs)

        self.closed = False
        self._internal_data = deque()
        self._children = deque()

        # self.next_element = None
        # self.previous_element = None

        self.vertical_position = 0
        self.horizontal_position = 0

        # An instance of the class that extracts
        # in order to be able to access other
        # items in the HTML tree
        # if not isinstance(extractor, Extractor):
        #     raise TypeError('Extractor should be an instance of Extractor')
        self._extractor_instance = extractor

        # self.parents = deque()
        # self.parent = None

    def __repr__(self):
        if self.attrs:
            return f'<{self.name} {self._attrs_to_string}>'
        return f'<{self.name}>'

    # def __str__(self):
    #     return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, value):
        return value == self.name

    def __getitem__(self, value):
        return self.attrs.get(value, None)

    @property
    def children(self):
        # return self._children
        return QuerySet.copy(self._children)

    @property
    def string(self) -> Union[str, None]:
        # When we have one item, return it,
        # otherwise, with multiple data elements
        # we cannot tell which element to refer
        # to then we should just return None
        if len(self._internal_data) == 1:
            return self._internal_data[0]
        return None

    @property
    def clean_string(self):
        return deep_clean(self.string)

    @property
    def _attrs_to_string(self):
        items = []
        for key, value in self.attrs.items():
            items.append(f'{key}="{value}"')
        return ''.join(items)

    @staticmethod
    def _build_attrs(attrs):
        attrs_dict = OrderedDict()
        for key, value in attrs:
            attrs_dict.setdefault(key, value)
        return attrs_dict

    def has_attr(self, name: str):
        return name in self.attrs.keys()

    def find(self, name: str, attrs: dict = {}):
        """Find a tag within the children of the tag"""
        result_to_return = None
        for child in self.children:
            if child.name == name:
                result_to_return = child
                break
        return result_to_return

    def find_all(self, name: str, attrs: dict = {}):
        """Find all of a certain tag within the children of the tag"""
        results_to_return = []
        for child in self.children:
            if child.name == name:
                results_to_return.append(child)
        return QuerySet.copy(results_to_return)


class Tag(BaseTag):
    pass


class StringMixin(QueryMixin):
    def __init__(self, data):
        self.name = None
        self.data = data
        self.closed = True

        self.horizontal_position = 0
        self.vertical_position = 0

        self.parents = []
        self.parent = None

    def __repr__(self):
        return self.data

    def __eq__(self, value):
        return self.data == value

    def __contains__(self, value):
        return value in self.data

    @property
    def string(self):
        return self.data

    def has_attr(self):
        return False

    def get_attr(self, name: str):
        return None


class NewLine(StringMixin):
    def __init__(self):
        super().__init__('\n')


class ElementData(StringMixin):
    def __init__(self, data):
        super().__init__(data)
        self.name = 'data'


class Comment(StringMixin):
    def __init__(self, data):
        super().__init__(data)
        self.name = 'comment'
