from typing import Generator, Iterator, List, Union

from zineb.html_parser.utils import filter_by_name_or_attrs
from zineb.utils.iteration import drop_while


class QuerySet:
    """Represents the aggregation of multiple
    tags from the html page"""
    
    def __init__(self):
        self._data = []
        self._queryset = []

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index):
        return self._queryset_or_internal_data[index]

    def __len__(self):
        return len(self._data)

    @classmethod
    def copy(cls, data: Union[Generator, Iterator]):
        instance = cls()
        instance._data = list(data)
        return instance

    @property
    def first(self):
        return self._data[0]

    @property
    def last(self):
        return self._data[-1]

    @property
    def count(self) -> int:
        return len(self._data)
    
    @property
    def _queryset_or_internal_data(self):
        # If the user has already run a query
        # on the previous or current queryset,
        # the logical move is to query the
        # new queryset and not the global data.
        # This function returns either the newly
        # created queryet if one exists
        # or the global data.
        return self._queryset or self._data

    def save(self, filename: str):
        pass

    def find(self, name: str, attrs: dict = {}):
        """Get a tag by name or attribute. If there are multiple
        tags, the first item of the list is returned"""
        result = filter_by_name_or_attrs(self._queryset_or_internal_data, name, attrs)
        return list(result)[0]

    def find_all(self, name: str, attrs: dict = {}):
        """Filter tags by name or by attributes"""
        result = filter_by_name_or_attrs(self._data, name, attrs)
        self._queryset = result
        return QuerySet.copy(result)

    def exclude(self, name: str, attrs: dict={}):
        """Exclude tags with a specific name or attributes"""
        values = []
        for item in self._queryset_or_internal_data:
            truth_array = [item.name != name]
            
            for attr, value in attrs.items():
                result = item.get_attr(attr)
                truth_array.append(result == value)
                
            if any(truth_array):
                values.append(item)
                
        return QuerySet.copy(values)

    def distinct(self, *attrs):
        """Return tags with a distinct attribute"""

    def values(self, *attrs: List[str], include_fields: bool=False):
        """Return the string or an attribute contained 
        for each tag in the queryset. By default, if no
        attribute is provided, the string is returned
        by defalult"""
        contents = []
        
        if not attrs:
            attrs.append('string')
        
        for item in self._queryset_or_internal_data:
            values = []
            for attr in attrs:
                if attr == 'string':
                    values.append(getattr(item, attr))
                else:
                    values.append(item[attr])
            contents.append(values)
            
        if include_fields:
            contents.insert(0, list(attrs))
        
        return contents
    
    def values_list(self, *attrs):
        """Returns a list of tuples using the provided 
        attributes e.g. [(('id', 'test'), ('data', 'test'))]
        """

    def dates(self, name: str = None):
        """If a tag is a date type e.g. <datetime /> or contains a date, this
        will transform the values within them to a list of python
        datetime objects"""

    def union(self, *querysets):
        """Combine the results of one or more querysets
        
        Example
        -------
        
            q1 = queryset.find_all('a')
            
            q2 = queryset.find_all('html')
            
            q3 = q1.union(q2)
        """
        results = []
        results.extend(self._queryset_or_internal_data)
        for queryset in querysets:
            if not isinstance(queryset, QuerySet):
                raise TypeError('Queryset is not an instance of Queryet')
            results.extend(queryset._queryset_or_internal_data)
        return self.copy(results)

    def exists(self):
        """Checks wheter there are any items in th quersyet"""
        return self.count > 0

    def contains(self, name: str):
        """Checks if a tag exists within the queryset"""
        results = []
        for item in self._queryset_or_internal_data:
            results.append(name == item)
        return any(results)

    def explain(self):
        """Returns explicit information about the items contained
        in the queryset e.g. link <a> with data ... x attributes"""
        for item in self._queryset_or_internal_data:
            msg = f"name: {item.name}, tag: {repr(item)}, data: {item.string}"
            print(msg)

    def generator(self, name: str, attrs: dict = {}):
        """Defers the evaluation of the query to a latter time"""
        return filter_by_name_or_attrs(self._queryset_or_internal_data, name , attrs)

    def update(self, name: str, attr: str, value: str):
        """Update the attribute list of a list of items
        within the queryset"""

    def filter(self, *funcs):
        """Function for running more complexe
        queries on the html page"""
        pass