from typing import Union, Generator, Iterator

class QuerySet:
    def __init__(self):
        self._data = []

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index):
        return QuerySet.copy(self._data[index])

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

    def save(self, filename: str):
        pass

    def find(self, name: str, attrs: dict = {}):
        pass

    def find_all(self, name: str, attrs: dict = {}):
        pass

    def exclude(self, name: str, attrs: dict = {}):
        """Exclude tags with a specific name or attributes"""

    def distinct(self, *attrs):
        """Return tags with a distinct attribute"""

    def values(self, *attrs):
        """Return the string contained for each tag in the queryset"""

    def dates(self, name: str = None):
        """If a tag is a date type e.g. <datetime /> or contains a date, this
        will transform the values within them to a list of python
        datetime objects"""

    def union(self, *querysets):
        """Combine the results of one or more querysets"""

    def exists(self):
        """Checks wheter there are any items in th quersyet"""
        return self.count > 0

    def contains(self, name: str):
        """Checks if a tag exists within the queryset"""

    def explain(self):
        """Returns explicit information about the items contained
        in the queryset e.g. link <a> with data ... x attributes"""

    def generator(self, name: str, attrs: dict = {}):
        """Defers the evaluation of the query to a later time"""
        return (x.name == name for x in self._data)
