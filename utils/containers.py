from collections import defaultdict
from operator import itemgetter

from zineb.models.fields import Empty
from zineb.utils.formatting import LazyFormat, remap_to_dict
from zineb.utils.iterations import drop_while


class SmartDict:
    """
    A container that regroups data under multiple keys by ensuring that
    when one key is updated, the other keys are in the same way therefore
    creating balanced data
    """

    current_updated_fields = set()

    def __init__(self, *fields, order_by=[]):
        self.values = defaultdict(list)
        self.fields = fields
        for field in fields:
            self.values[field]

        self._last_created_row = []

        self._id = 0
        self.order_by = order_by

    def __repr__(self):
        return str(dict(self.values))

    def __str__(self):
        return str(self.as_list())

    @classmethod
    def new_instance(cls, *fields):
        return cls(*fields)

    def _last_value(self, name):
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

        if name not in self.fields:
            raise ValueError(LazyFormat("Field '{field}' is not present "
                                        "on the declared container fields.", field=name))

        def row_generator():
            # Generate a new list of values for all
            # the fields. For example if we have
            # fields name, surname then we'll get
            # a list [value_for_name, value_for_surname]
            for _, field_name in enumerate(self.fields, start=1):
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
            for i, field_name in enumerate(self.fields, start=1):
                container = self.get_container(field_name)
                container.append(self._last_created_row[i - 1])
            self._id = self._id + 1
        else:
            self.current_updated_fields.add(name)
            if self._last_created_row:
                for i, field_name in enumerate(self.fields, start=1):
                    if field_name == name:
                        value_to_update = [self._last_created_row[i - 1]]
                        value_to_update[-1] = value
                        self.update_last_item(
                            field_name, tuple(value_to_update))
            else:
                self._last_created_row = list(row_generator())
                # Based on the position of the field name in the
                # field_names, return the corresponding value that
                # we got from the generated row
                for i, field_name in enumerate(self.fields, start=1):
                    container = self.get_container(field_name)
                    container.append(self._last_created_row[i - 1])
                self._id = self._id + 1
            # self.run_constraints(container)

    def update_multiple(self, attrs: dict):
        for key, value in attrs.items():
            self.update(key, value)

    def apply_sort(self, values):
        """Sorting method needs to be introduced
        by the subclasses"""
        return values

    def as_values(self):
        """
        Returns the data as dictionnary

        >>> {key1: [..., ...], key2: [..., ...], ...}
        """
        return self.values

    def as_list(self):
        """
        Return a sorted collection of dictionnaries

        >>> [{a: 1}, {b: 2}, ...]
        """
        values = remap_to_dict(self.as_values())
        return self.apply_sort(values)

    def as_csv(self):
        """
        Return the values under a csv format

        >>> [[col1, col2], [..., ...]]
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


class ModelSmartDict(SmartDict):
    """A SmartDict that is bound to a model"""

    def __init__(self, model, order_by=[], include_id_field=False):
        fields = model._meta.field_names
        super().__init__(*fields, order_by=order_by)
        self.include_id_field = include_id_field
        self.model = model
        new_fields = list(drop_while(
            lambda x: x == 'id' and not self.include_id_field, fields))
        self.fields = new_fields

    @classmethod
    def new_instance(cls, model, **kwargs):
        return cls(model, **kwargs)

    def apply_sort(self, values):
        has_ordering = self.model._meta.has_ordering
        if has_ordering:
            ordering = self.model._meta.get_ordering()
            ordering_booleans = ordering.booleans
        else:
            has_ordering = len(self.order_by) > 0
            # For the ordering to work, we need a list
            # of dicts as [(field_name, True), ...].
            # The boolean determines whether the sort
            # is ascending or descending.
            for item in self.order_by:
                if not isinstance(item, (list, tuple)):
                    raise ValueError(
                        'Ordering method should be either an array or a tuple')

                _, value = item
                if not isinstance(value, bool):
                    raise TypeError(
                        'Ordering direction for needs to be a boolean')

            ordering_booleans = self.order_by

        if has_ordering:
            def multisort(values, sorting_methods):
                for key, reverse in reversed(sorting_methods):
                    values.sort(key=itemgetter(key), reverse=reverse)
                    return values
            return multisort(values, ordering_booleans)
        return values
