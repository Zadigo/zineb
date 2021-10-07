from collections import defaultdict
from typing import Any, List
import copy
import datetime
import secrets
from zineb.models.fields import Empty


class SmartDict:
    """
    A container that regroups data under multiple keys by ensuring that
    when one key is updated, the other keys are too ensuring that all
    containers a balanced
    
        container = SmartDict('name', 'surname')
        
        container.update('name', 'Kendall')
        {'name': ['Kendall'], 'surname': [None]}

        container.update('name', 'Kylie')
        container.update('surname', 'Jenner')
        {'name': ['Kendall', 'Kylie'], 'surname': [None, 'Jenner']}
    """
    current_updated_fields = set()

    def __init__(self, *fields):
        self.values = defaultdict(list)
        for field in fields:
            self.values[field]
        setattr(self, 'field_names', list(fields))
        self._last_created_row = []

    def __repr__(self):
        return self.values

    def __str__(self):
        return str(dict(self.as_values()))

    def copy(self):
        return copy.copy(self.values)

    # @classmethod
    # def as_container(cls, *names):
    #     instance = cls()
    #     for name in names:
    #         instance.values[name]
    #     setattr(instance, 'names', list(names))
    #     return instance
        
    @property
    def _last_id(self) -> int:
        """
        Returns the last registered ID within
        the first container
        """
        container = self.get_container(self.field_names[0])
        if not container:
            return 0
        return container[-1][0]

    def _last_value(self, name: str):
        return self.get_container(name)[-1][-1]

    @property
    def _next_id(self):
        return self._last_id + 1

    def get_container(self, name: str):
        return self.values[name]

    def update_last_item(self, name: str, value: Any):
        container = self.get_container(name)
        if isinstance(value, tuple):
            container[-1] = value
        else:
            # TODO: Check that the id is correct
            container[-1] = (self._last_id, value)

    def update(self, name: str, value: Any):
        """
        Generates a new row and then implements them on
        the overall data placeholder
        """
        if value == Empty:
            value = None

        def row_generator():
            # Generate a new row of values that will be
            # added to the overall data container
            # e.g. (id, value) or (id, None)
            for _, field_name in enumerate(self.field_names, start=1):
                if name == field_name:
                    yield (self._next_id, value)
                else:
                    yield (self._next_id, None)

        if name in self.current_updated_fields:
            self.current_updated_fields.clear()
            self.current_updated_fields.add(name)
            self._last_created_row = None
            
            self._last_created_row = list(row_generator())

            # Iterate over each values that were created and with
            # the index of returned by enumerate, append tuple
            # to their corresponding containers
            for i, field_name in enumerate(self.field_names, start=1):
                self.get_container(field_name).append(self._last_created_row[i - 1])
        else:
            self.current_updated_fields.add(name)
            if self._last_created_row:
                for i, field_name in enumerate(self.field_names, start=1):
                    if field_name == name:
                        value_to_update = list(self._last_created_row[i - 1])
                        value_to_update[-1] = value
                        self.update_last_item(field_name, tuple(value_to_update))
            else:
                self._last_created_row = list(row_generator())
                for i, field_name in enumerate(self.field_names, start=1):
                    self.get_container(field_name).append(self._last_created_row[i - 1])

    def update_multiple(self, attrs: dict):
        for key, value in attrs.items():
            container = self.get_container(key)
            container.append((self._next_id, value))

    def as_values(self):
        """
        Return collected values by removing the index part 
        in the tuple e.g [(1, ...), ...] becomes [..., ...]
        """
        container = {}
        for key, values in self.values.items():
            values_only = map(lambda x: x[-1], values)
            container.update({key: list(values_only)})
        return container


class SimpleMultiDict(dict):
    """
    A simple dictionnary that can store multiple values
    one key as a list.

        SimpleMultiDict({'name': [], 'surname': []})
    """
    def __init__(self, *keys):
        mappings = [(key, []) for key in keys]
        super().__init__(mappings)

    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'

    def __getitem__(self, key):
        try:
            result = super().__getitem__(key)
        except KeyError:
            raise KeyError('Key does not exist')
        else:
            return result

    def __setitem__(self, key, value):
        super().__setitem__(key, [value])

    def items(self):
        for key in self:
            yield key, self[key]

    def values(self):
        for key in self:
            yield self[key]

    def get_container(self, key) -> List:
        return self.__getitem__(key)

    def container_exists(self, key):
        if key in self:
            return True

    def append(self, key, value):
        container = self.get_container(key).append(value)

    def update(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.get_container(key).append(value)




# c = SimpleMultiDict('name', 'surname')
# c.update(name='Kendall', surname='Kendall')
# print(c)

c = SmartDict('name', 'surname')
c.update('name', 'Kendall')
c.update('name', 'Kylie')
c.update('surname', 'Jenner')
print(c)
