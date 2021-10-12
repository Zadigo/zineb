import copy
import csv
import datetime
import json
import os
import secrets
from collections import defaultdict
from typing import Any

from zineb.models.fields import Empty
from zineb.settings import lazy_settings
from zineb.utils.formatting import remap_to_dict

from utils.formatting import LazyFormat


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

    @classmethod
    def new_instance(cls, *names):
        instance = cls(*names)
        for name in names:
            instance.values[name]
        setattr(instance, 'names', list(names))
        return instance

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

        if name not in self.field_names:
            raise ValueError(LazyFormat("Field '{field}' is not present "
            "on the declared container fields.", field=name))

        def row_generator():
            # Generate a new row of values that will be
            # added to the overall data container
            # e.g. (id, value) or (id, None)
            for _, field_name in enumerate(self.field_names, start=1):
                if name == field_name:
                    yield (self._next_id, value)
                else:
                    yield (self._next_id, None)

        # When the name is already present
        # in current_updated_fields, it means
        # that we creating/updating a new row
        if name in self.current_updated_fields:
            self.current_updated_fields.clear()
            self.current_updated_fields.add(name)
            self._last_created_row = None
            
            self._last_created_row = list(row_generator())

            # Iterate over each values that were created and with
            # the index returned by enumerate, append tuple
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
            self.update(key, value)

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

    def as_list(self):
        """
        Return a collection of dictionnaries
        e.g. [{a: 1}, {a: 2}, ...]
        """
        return remap_to_dict(self.as_values())

    def as_csv(self):
        """Return scrapped values to be written
        to a CSV file"""
        data = self.as_values()
        base = [list(data.keys())]
        for _, values in data.items():
            base.append(values)
        return base

    def save(self, commit: bool=True, filename: str=None, extension='json', **kwargs):
        extensions = ['json', 'csv']
        if extension not in extensions:
            raise ValueError(LazyFormat('Extension {extension} is not valid.', extension=extension))

        if commit:
            filename = filename or secrets.token_hex(5)
            filename = f'{filename}.{extension}'
            try:
                # If the MEDIA_FOLDER setting is None still allow
                # saving the file in the local directory
                path = os.path.join(lazy_settings.MEDIA_FOLDER, f'{filename}')
            except:
                path = filename

            if extension == 'json':
                data = json.loads(json.dumps(self.as_list()))
                with open(path, mode='w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, sort_keys=True)

            if extension == 'csv':
                with open(path, mode='w', newline='\n', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(self.as_csv())
        else:
            data = json.loads(json.dumps(self.as_list()))
            return json.dumps(data, sort_keys=True)
