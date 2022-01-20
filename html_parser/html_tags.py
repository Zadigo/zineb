from collections import OrderedDict, deque
from functools import cached_property
from typing import Callable, List, Tuple, Union

from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.utils import break_when, filter_by_name
from zineb.utils.characters import deep_clean
from zineb.utils.iteration import drop_while


class QueryMixin:
    @property
    def _has_extractor(self):
        return self._extractor_instance is not None

    @property
    def previous_element(self):
        """Returns the element directly before this tag"""
        def filtering_function(x):
            return x.index == self.index - 1
        return break_when(filtering_function, self._extractor_instance)

    @property
    def next_element(self):
        """Returns the element directly next to this tag"""
        def filtering_function(x):
            return x.index == self.index + 1
        return break_when(filtering_function, self._extractor_instance)
    
    @property
    def contents(self):
        """Returns all the data present
        within the tag"""
        return []
    
    @property
    def attrs_list(self):
        """Return the attribute keys
        that are present on the tag"""
        return list(self.attrs)

    @cached_property    
    def parents(self):
        """List of parents for the tag"""
        return self._parents
    
    @cached_property
    def parent(self):
        """Parent for the tag"""
        return self.parents[-1]
    
    def get_attr(self, name: str) -> Union[str, None]:
        """Returns the value of an attribute"""
        return self.attrs.get(name, None)

    def get_previous(self, name: str):
        """Get the previous element in 
        respect to the name"""
        try:
            return list(self.get_all_previous(name))[-1]
        except:
            return None
         
    def get_next(self, name: str):
        """Get the next element in 
        respect to the name"""
        try:
            return list(self.get_all_next(name))[-1]
        except:
            return None
        
    def get_all_previous(self, name: str):
        """Get all the previous elements in
        respect to the name"""
        if not self._has_extractor:
            raise TypeError('To use to query with tags, need an extractor')
        
        with self._extractor_instance as items:
            for item in items:
                if item.name == name:
                    if item.index < self.index:
                        yield item
    
    def get_all_next(self, name: str):
        """Get all the next elements in
        respect to the name"""
        if not self._has_extractor:
            raise TypeError('To use to query with tags, need an extractor')
        
        with self._extractor_instance as items:
            for item in items:
                if item.name == name:
                    if item.index > self.index:
                        yield item
        
    def children(self, **attrs):
        pass
    
    def get_parent(self, name: str):
        """Return a specific parent from list
        of available parents"""
        result = filter_by_name(self.parents, name)
        return list(result)[-1]
    
    def get_previous_sibling(self, name: str):
        pass

    def get_next_sibling(self, name: str):
        pass


class BaseTag(QueryMixin):
    """Base class for all HTML tags"""
    
    def __init__(self, name: str, attrs: List[Tuple[str, str]]=[], extractor: Callable=None):
        self.name = name
        self.attrs = self._build_attrs(attrs)

        self.closed = False
        self._internal_data = deque()
        self._children = deque()

        self.vertical_position = 0
        self.horizontal_position = 0
        self.index = 0

        # An instance of the class that extracts
        # in order to be able to access other
        # items in the HTML tree
        # if not isinstance(extractor, Extractor):
        #     raise TypeError('Extractor should be an instance of Extractor')
        self._extractor_instance = extractor
        
        self._parents = []

    def __repr__(self):
        if self.attrs:
            return f'<{self.name} {self._attrs_to_string}>'
        return f'<{self.name}>'

    def __hash__(self):
        attrs = ''.join(self.attrs.values())
        return hash((self.name, self.index, attrs))

    def __eq__(self, value):
        # truth_array = [value in list(self.attrs.values()), value == self.name]
        # return any(truth_array)
        return value == self.name

    def __getitem__(self, value):
        if not isinstance(value, str):
            raise ValueError('Value to compare should be a string')
        return self.attrs.get(value, None)
    
    def __contains__(self, value):
        values = self.attrs.values()
        return value in self.name or value in values

    @property
    def children(self):
        # return self._children
        return QuerySet.copy(self._children)

    @property
    def string(self):
        # When we have one item, return it,
        # otherwise, with multiple data elements
        # we need a specific logic to determine
        # exactly what to return...
        if len(self._internal_data) == 1:
            return self._internal_data[0]
        
        # In a case where we have one solid
        # string data an only null strings,
        # then we should return that item
        result = list(drop_while(lambda x: x == '\n', self._internal_data))
        if result:
            return result[-1]
        
        return None

    @property
    def clean_string(self):
        return deep_clean(self.string)

    @cached_property
    def _attrs_to_string(self):
        items = []
        for key, value in self.attrs.items():
            items.append(f'{key}="{value}"')
        return ' '.join(items)

    @staticmethod
    def _build_attrs(attrs):
        attrs_dict = OrderedDict()
        for key, value in attrs:
            attrs_dict.setdefault(key, value)
        return attrs_dict

    def has_attr(self, name: str):
        """Checks if a tag has a specific attribute"""
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
    """Represents an HTML tag"""


class StringMixin(QueryMixin):
    def __init__(self, data, extractor=None):
        self.name = None
        self.data = data
        self.closed = True

        self.vertical_position = 0
        self.horizontal_position = 0
        self.index = 0
        
        self._extractor_instance = extractor

        self._parents = []

    def __repr__(self):
        return self.data

    def __eq__(self, value):
        return self.data == value

    def __contains__(self, value):
        return value in self.data
    
    def __add__(self, value):
        return self.data + str(value)
    
    def __hash__(self):
        return hash((self.name, self.data, self.index))

    @property
    def string(self):
        return self.data

    def has_attr(self, name: str):
        return False

    def get_attr(self, name: str):
        return None


class NewLine(StringMixin):
    """Represents a newline as \\n"""
    
    def __init__(self, extractor=None):
        super().__init__('\n', extractor=extractor)
        self.name = 'newline'
        
    def __eq__(self, value):
        return value == '\n'
    
    def __repr__(self):
        return '\\n'
    
    def __hash__(self):
        return hash((self.name, self.data))
                

class ElementData(StringMixin):
    """Represents a data element within
    a tag e.g. Kendall in <span>Kendall</span>"""
    
    def __init__(self, data, extractor=None):
        super().__init__(data, extractor=extractor)
        self.name = 'data'


class Comment(StringMixin):
    """Represents a comment"""
    
    def __init__(self, data, extractor=None):
        super().__init__(data, extractor=extractor)
        self.name = 'comment'
