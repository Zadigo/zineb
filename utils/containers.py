import csv
import json
import os
import secrets
from collections import defaultdict
from operator import itemgetter
from pathlib import Path

from zineb.models.fields import Empty
from zineb.settings import settings
from zineb.utils.formatting import LazyFormat, remap_to_dict

class SmartDict:
    """
    A container that regroups data under multiple keys by ensuring that
    when one key is updated, the other keys are in the same way therefore
    creating balanced data
    """

    current_updated_fields = set()

    def __init__(self, *fields):
        self.model = None
        self.values = defaultdict(list)

        for field in fields:
            self.values[field]
            
        self._last_created_row = []
        
        self._id = 0

    def __repr__(self):
        return self.values

    def __str__(self):
        return str(self.as_list())

    @classmethod
    def new_instance(cls, model):
        field_names = model._meta.field_names
        instance = cls(*field_names)
        instance.model = model
        return instance

    def _last_value(self, name: str):
        return self.get_container(name)[-1][-1]

    def get_container(self, name: str):
        return self.values[name]

    def update_last_item(self, name: str, value):
        container = self.get_container(name)
        if isinstance(value, tuple):
            container[-1] = value[-1]
        else:
            container[-1] = (value)

    def update(self, name, value):
        """
        Generates a new row and then implements them on
        the overall data placeholder
        """
        if value == Empty:
            value = None

        if name not in self.model._meta.field_names:
            raise ValueError(LazyFormat("Field '{field}' is not present "
            "on the declared container fields.", field=name))

        def row_generator():
            # Generate a new list of values for all
            # the fields. For example if we have
            # fields name, surname then we'll get
            # a list [value_for_name, value_for_surname]
            for _, field_name in enumerate(self.model._meta.field_names, start=1):
                if name == field_name:
                    yield (value)
                else:
                    yield (None)

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
            for i, field_name in enumerate(self.model._meta.field_names, start=1):
                container = self.get_container(field_name)
                container.append(self._last_created_row[i - 1])
            self._id = self._id + 1
        else:
            self.current_updated_fields.add(name)
            if self._last_created_row:
                for i, field_name in enumerate(self.model._meta.field_names, start=1):
                    if field_name == name:
                        value_to_update = [self._last_created_row[i - 1]]
                        value_to_update[-1] = value
                        self.update_last_item(field_name, tuple(value_to_update))
            else:
                self._last_created_row = list(row_generator())
                # Based on the position of the field name in the
                # field_names, return the corresponding value that
                # we got from the generated row
                for i, field_name in enumerate(self.model._meta.field_names, start=1):
                    container = self.get_container(field_name)
                    container.append(self._last_created_row[i - 1])
                self._id = self._id + 1

    def update_multiple(self, attrs: dict):
        for key, value in attrs.items():
            self.update(key, value)
            
    def apply_sort(self, values):
        if self.model._meta.has_ordering:
            def multisort(values, sorting_methods):
                for key, reverse in reversed(sorting_methods):
                    values.sort(key=itemgetter(key), reverse=reverse)
                    return values
            ordering = self.model._meta.get_ordering()
            return multisort(values, ordering.booleans)
        return values

    def as_values(self):
        """
        Returns the data as
        {key1: [..., ...], key2: [..., ...], ...}
        """
        return self.values

    def as_list(self, include_index=False):
        """
        Return a collection of dictionnaries
        e.g. [{a: 1}, {b: 2}, ...]
        """
        values = remap_to_dict(self.as_values())
        return self.apply_sort(values)

    def as_csv(self):
        """
        Return the values under a csv format
        as [[col1, col2], [..., ...]]
        """
        data = self.as_values()
        columns = list(data.keys())
        base = [columns]

        last_column = columns[-1]
        number_of_items = len(data[last_column])
        # Create the amount of rows that will be 
        # necessary for a single column
        canvas = [[] for _ in range(number_of_items)]

        for column in data.values():
            for i, row_value in enumerate(column):
                canvas[i].append(row_value)
        base.extend(canvas)
        return base

    def execute_save(self, commit: bool=True, filename: str=None, extension: str='json', **kwargs):
        if commit:
            filename = filename or secrets.token_hex(5)
            filename = f'{filename}.{extension}'
            
            try:
                path = Path(settings.MEDIA_FOLDER)
                if not path.exists():
                    path.mkdir()
            except:
                path = filename

            file_path = os.path.join(settings.MEDIA_FOLDER, f'{filename}')
            if extension == 'json':
                data = json.loads(json.dumps(self.as_list()))
                with open(file_path, mode='w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, sort_keys=True)

            if extension == 'csv':
                with open(file_path, mode='w', newline='\n', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(self.as_csv())
        else:
            data = json.loads(json.dumps(self.as_list()))
            return json.dumps(data, sort_keys=True)
