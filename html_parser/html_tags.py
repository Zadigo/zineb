from collections import OrderedDict, deque
from functools import cached_property
from typing import Callable, Iterator, List, Tuple, Union

from zineb.html_parser.queryset import QuerySet
from zineb.html_parser.utils import (SELF_CLOSING_TAGS, break_when,
                                     filter_by_name, filter_by_names)
from zineb.utils.characters import deep_clean
from zineb.utils.iteration import drop_while, keep_while


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
        
    def get_children(self, *names):
        """Return children by names contained
        within the tag. If no name is provided,
        returns all of them"""
        items = filter_by_names(self._children, names)
        return QuerySet.copy(items)
    
    def get_parent(self, name: str):
        """Return a specific parent from list
        of available parents"""
        result = filter_by_name(self.parents, name)
        return list(result)[-1]
    
    def get_previous_sibling(self, name: str):
        pass

    def get_next_sibling(self, name: str):
        pass
    
    def delete(self):
        pass

    def insert_before(self, *tags):
        pass

    def insert_after(self, *tags):
        pass

    def insert_data(self, data: str):
        pass

    def update_attr(self, attr: str, value: str):
        """Update the attributes of all the tags
        within the queryset"""
        self.attrs.update({attr: value})

    def update_data(self, data: str):
        pass


class TagMixin:
    def __init__(self, name, attrs=[], extractor=None):
        self.name = name
        
        self.closed = False
        
        self.attrs = self._build_attrs(attrs)
            
        self._previous_sibling = None
        self._next_sibling = None
        
        self._coordinates = []
        
        self.index = 0
        
        self._parents = []
        self._children = deque()
        
        # An instance of the class that extracts
        # in order to be able to access other
        # items in the HTML tree
        from zineb.html_parser.extractors import Extractor
        if extractor is not None:
            if not isinstance(extractor, Extractor):
                raise TypeError('Extractor should be an instance of Extractor')
        self._extractor_instance = extractor

        
    #     self._internal_data = deque()        
    
    @cached_property
    def _attrs_to_string(self):
        if not self.attrs:
            return ''
        else:
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
    
    # def to_html(self):
    #     """
    #     Show the html representation
    #     of the current tag and its children
    #     """
    #     if self.name in SELF_CLOSING_TAGS:
    #         template = "<{name}{attrs}>"
    #         return template.format(name=self.name, attrs=self._attrs_to_string)
    #     else:
    #         template = "<{name}{attrs}>{content}</{name}>"
            
    #         tag_data = ''.join(self._internal_data)
            
    #         children_representations = map(
    #             lambda x: x.to_html(), self.children)
    #         children = ''.join(children_representations)
            
    #         content = tag_data + children
            
    #         return template.format(name=self.name, attrs=self._attrs_to_string, content=content)


class BaseTag(TagMixin, QueryMixin):
    """Base class for HTML tags"""
    
    def __init__(self, name: str, attrs: List[Tuple[str, str]]=[], extractor: Callable=None):
        super().__init__(name, attrs, extractor=extractor)
        self._internal_data = deque()
        
    def __repr__(self):
        if self.attrs:
            return f'<{self.name} {self._attrs_to_string}>'
        return f'<{self.name}>'

    def __hash__(self):
        attrs = ''.join(self.attrs.values())
        return hash((self.name, self.index, attrs))

    def __eq__(self, obj):
        logic = [obj.name == self.name, obj.attrs == self.attrs]
        return all(logic)
    
    def __ne__(self, obj):
        return self.name != obj.name

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise ValueError('Value should be a string. Got:')
        return self.attrs.get(key, None)
    
    def __setitem__(self, key, value):
        self.attrs[key] = value
    
    def __delitem__(self, key):
        del self.attrs[key]
    
    def __contains__(self, name_or_obj):
        return name_or_obj in self.children

    @property
    def children(self):
        return QuerySet.copy(self._children)

    @property
    def string(self):
        # When we have one item, return it,
        # otherwise, with multiple data elements
        # we use a specific logic to determine
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
    
    def find(self, name: str, attrs: dict = {}):
        """Find a tag within the children of the tag"""
        result_to_return = None
        for child in self.children:
            if child.name == name:
                result_to_return = child
                break
        return result_to_return

    def find_all(self, name: str, attrs: dict = {}, limit: int=None):
        """Find all elements that match a given tag name
        or attribute within the children elements
        of the tag"""
        results_to_return = []
        for child in self.children:
            if child.name == name:
                results_to_return.append(child)
        return QuerySet.copy(results_to_return)


class Tag(BaseTag):
    """Represents an HTML tag"""


class StringMixin(TagMixin, QueryMixin):        
    def __str__(self):
        return self.data

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

    @cached_property
    def _attrs_to_string(self):
        return ''
    
    @cached_property
    def get_children(self, *names):
        """String tags will always return a empty
        QuerySet because they are not supposed to
        have any children"""
        return QuerySet.copy([])
    
    @staticmethod
    def _build_attrs(attrs):
        # String tags have no attrs and
        # should therefore not be able
        # to build them - the same goes
        # has_attr and get_attr
        return {}

    def has_attr(self, name: str):
        return False

    def get_attr(self, name: str):
        return None
    

class NewLine(StringMixin):
    """Represents a newline as \\n"""
    
    def __init__(self, extractor: Callable=None):
        super().__init__('newline', extractor=extractor)
        self.closed = True
        self.data = '\n'
        
    def __eq__(self, value):
        return value == '\n'
    
    def __repr__(self):
        return '\\n'
                    

class ElementData(StringMixin):
    """Represents a data element within
    a tag e.g. Kendall in <span>Kendall</span>"""
    
    def __init__(self, data, extractor: Callable=None):
        super().__init__('data', extractor=extractor)
        self.closed = True
        self.data = data


class Comment(StringMixin):
    """Represents a comment"""
    
    def __init__(self, data, extractor: Callable=None):
        super().__init__('comment', extractor=extractor)
        self.name = 'comment'
        self.data = data
