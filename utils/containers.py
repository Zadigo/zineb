from collections import defaultdict
from functools import cached_property, total_ordering
from operator import itemgetter

from zineb.exceptions import IntegrityError


class Synchronizer:
    """A class that can synchronize multiple
    columns together and therefore allows balanced
    rows between each elements of the container
    """

    def __init__(self, columns):
        self.columns = columns
        self._field_names = columns.smart_dict.fields
        self.column_rows = []
        self.current_updated_columns = set()

    def __repr__(self):
        return f'<{self.__class__.__name__}(columns={len(self.columns)})>'

    @property
    def get_last_row(self):
        try:
            return self.column_rows[-1]
        except:
            return False

    def enforce_uniqueness(self, last_row):
        """Each row ID should be unique in
        the same manner that we get in a database"""
        last_row_id = last_row['id']
        raise_integrity_error = False

        if len(self.column_rows) == 1:
            if last_row_id == self.column_rows[0]['id']:
                raise_integrity_error = True

        if len(self.column_rows) > 1:
            if last_row_id in self.column_rows:
                raise_integrity_error = True

        if raise_integrity_error:
            message = (f"A row with id '{last_row_id}' was already "
                       f"present in the container: {last_row}")
            raise IntegrityError(message)

    def synchronize(self, current_column, column_rows):
        """Ensure that each columns knows about the
        current rows in the container in order to
        create a balanced output"""
        # FIXME: When trying to enforce uniqueness,
        # self.column_rows get automatiically updated
        # with the new values while the function to
        # update its new values is behind the
        # column_rows function
        # self.enforce_uniqueness(column_rows[-1])
        self.column_rows = column_rows
        for column in self.columns:
            if column == current_column:
                continue
            setattr(column, 'column_rows', column_rows)


class Columns:
    """Represents a collection of columns

    >>>    ID    col1    col2
    ...     1      A       B

    Our columns here are `[col1, col2]`
    """

    def __init__(self, smart_dict):
        self.smart_dict = smart_dict
        self.model = getattr(smart_dict, 'model', None)
        self.declared_fields = list(smart_dict.fields)
        self.columns = [
            Column(self, i, field_name)
            for i, field_name in enumerate(self.declared_fields)
        ]
        self.synchronizer = Synchronizer(self)

    def __repr__(self):
        columns = ', '.join([repr(column) for column in self.columns])
        return f'<{self.__class__.__name__}[{columns}]>'

    def __iter__(self):
        for column in self.columns:
            yield column

    def __len__(self):
        return len(self.first)

    @cached_property
    def number_of_items(self):
        return len(self.first)

    @cached_property
    def as_values(self):
        values = defaultdict(list)
        for column in self.columns:
            values[column._field_name] = column.get_column_values
        return values

    @cached_property
    def as_records(self):
        items = []
        for row in self.synchronizer.column_rows:
            items.append(row.row_values)
        return items

    @cached_property
    def as_csv(self):
        template = [list(self.declared_fields)]
        for row in self.synchronizer.column_rows:
            csv_row = []
            for field in self.declared_fields:
                csv_row.append(row[field])
            template.append(csv_row)
        return template

    @cached_property
    def first(self):
        try:
            return self.columns[-0]
        except:
            return None

    @cached_property
    def last(self):
        try:
            return self.columns[-1]
        except:
            return None

    def get_column(self, name):
        result = list(filter(lambda x: x == name, self.columns))
        if not result:
            pass
        return result[-1]


class Column:
    """Represents a single column for a collection
    of columns in the data container

    >>> column = Column(columns, 1, "name")
    ... column.column_values
    ... ["Kendall jenner", "Kylie Jenner", ...]
    ... column.column_rows
    ... [Row({id: 1, name: "Kendall Jenner"})]
    """

    def __init__(self, columns_instance, index, field_name):
        self.index = index

        self._field_name = field_name
        self._column_name = field_name.title()
        self._columns_instance = columns_instance

        self.smart_dict = self._columns_instance.smart_dict
        self.column_rows = []
        self.colum_values = []

    def __repr__(self):
        return f'<Column: {self._column_name}>'

    def __eq__(self, name):
        return self._field_name == name

    def __hash__(self):
        return hash((self._field_name, self.index))

    def __len__(self):
        return len(self.colum_values)

    @cached_property
    def get_column_values(self):
        def evaluate():
            for column in self.column_rows:
                yield column[self._field_name]
        return list(evaluate())

    @cached_property
    def get_row_values(self):
        items = {}
        for row in self.column_rows:
            for field in self.smart_dict.fields:
                items[field] = row[field]
        return items

    def add_new_row(self, name, value, id_value=None):
        creation = True
        synchronizer = self._columns_instance.synchronizer
        if name in synchronizer.current_updated_columns:
            # If the name is in the current_updated_columns,
            # we know that we are creating a new row
            creation = True
            synchronizer.current_updated_columns.clear()
            synchronizer.current_updated_columns.add(name)
            row = Row(id_value, name, value, self.smart_dict.fields)
        elif name not in synchronizer.current_updated_columns:
            # In another case, we have to update the last
            # created with the values provided
            if len(synchronizer.current_updated_columns):
                creation = False
                row = synchronizer.get_last_row
                row.update_column_value(name, value)
            else:
                creation = True
                row = Row(id_value, name, value, self.smart_dict.fields)
            synchronizer.current_updated_columns.add(name)

        if creation:
            self.column_rows.append(row)
            self.colum_values.append(value)

        # When we create or update a row, the other columns do not
        # anything about said action. With the Synchronizer
        # class, we can tell each column to update themselves
        # continuously with the new data
        self._columns_instance.synchronizer.synchronize(name, self.column_rows)


@total_ordering
class Row:
    """Represents a row and all the values present
    in the on that specific line

    >>>    ID    col1    col2
    ...     1      A       B

    The row here represents therefore `[1, A, B]`

    >>> row = Row(1, "fullname", "Kendall Jenner")
    ... {"id": 1, "fullname": "Kendall Jenner"}
    """
    field_id = 1

    def __init__(self, field_id, field_name, field_value, fields):
        self._declared_fields = fields
        self.field_id = field_id
        self.row_values = {
            'id': field_id,
            field_name: field_value
        }

        for field in fields:
            if field == field_name:
                continue
            self.row_values[field] = None

    def __repr__(self):
        return f'<Row: [{self.row_values}]>'

    def __getitem__(self, column):
        return self.row_values[column]

    def __eq__(self, item):
        if isinstance(item, Row):
            return item.field_id == self.field_id
        return self.field_id == item

    def __gt__(self, item):
        if isinstance(item, Row):
            return item.field_id > self.field_id
        return self.field_id >= item

    def __contains__(self, value):
        return str(value) in str(self.field_id)

    def update_column_value(self, name, value):
        self.row_values[name] = value


class SmartDict:
    """
    A container that regroups data under multiple keys by ensuring that
    when one key is updated, the other keys are in the same way therefore
    creating balanced data.

    The data creation and updating proces uses the synchronous step-by-step 
    state of Python to add data to the container. In order words, if the field name
    of the next value in is different from the field name of the previous value in,
    a new row is created otherwise the last row is updated.

    This first example shows how adding a value to the field "name" and nothing
    to the field "surname" still creates a balanced output:

    >>> instance = SmartDict("name", "surname")
    ... instance.update("name", "Kendall")
    ... str(instance)
    ... [{"name": "Kendall Jenner", "surname": None}]

    This example shows when the user adds both fields:

    >>> instance.update("name", "Kendall")
    ... instance.update("surname", "Jenner")
    ... str(instance)
    ... [{"name": "Kendall Jenner", "surname": "Jenner"}]

    Multiple values can be updated at once:

    >>> instance.update_multiple({"name": "Kendall", "surname": "Jenner"})
    """

    def __init__(self, *fields, order_by=[]):
        self.fields = fields
        self.order_by = order_by
        self.columns = Columns(self)

    def __repr__(self):
        return f'<{self.__class__.__name__}[{self.as_list()}]>'

    def __str__(self):
        return str(self.as_list())

    @classmethod
    def new_instance(cls, *fields):
        return cls(*fields)

    def update(self, name, value, id_value=None):
        column = self.columns.get_column(name)
        column.add_new_row(name, value, id_value=id_value)

    def update_multiple(self, attrs):
        for key, value in attrs.items():
            self.update(key, value)

    def apply_sort(self, values):
        """Sorting method needs to be introduced
        by the subclasses"""
        return values


class ModelSmartDict(SmartDict):
    """A SmartDict that is bound to a model"""

    def __init__(self, model, order_by=[]):
        fields = model._meta.field_names
        super().__init__(*fields, order_by=order_by)
        self.model = model

    def __repr__(self):
        return f'<{self.__class__.__name__}(for={self.model._meta.verbose_name})>'

    @classmethod
    def new_instance(cls, model, **kwargs):
        return cls(model, **kwargs)

    def update(self, name, value):
        auto_id_field = self.model.update_id_field()
        super().update(name, value, id_value=auto_id_field._cached_result)

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


s = SmartDict('name', 'age')

# Test 1: name, name, age
# s.update('name', 'Kendall Jenner', id_value=1)
# s.update('name', 'Kylie Jenner', id_value=2)
# s.update('age', 21, id_value=2)

# Test 2: name, age, name
# s.update('name', 'Kendall Jenner', id_value=1)
# s.update('age', 21, id_value=2)
# s.update('name', 'Kylie Jenner', id_value=2)

# Test 3: name, age, name, age
# s.update('name', 'Kendall Jenner', id_value=1)
# s.update('age', 21, id_value=1)
# s.update('name', 'Kylie Jenner', id_value=2)
# s.update('age', 28, id_value=2)

# Test 4: Integrity
s.update('name', 'Kendall Jenner', id_value=1)
s.update('name', 'Anya Taylor Joy', id_value=2)
s.update('name', 'Kylie Jenner', id_value=1)


# FIXME: We can add a similar ID key in
# the columns

print(s.columns.as_records)
