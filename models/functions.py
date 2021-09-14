import datetime
from typing import Any, Callable, Union

from zineb.exceptions import ModelNotImplementedError
from zineb.utils.conversion import string_to_number
from zineb.utils.formatting import LazyFormat


class ExpressionMixin:
    model = None
    _cached_data = None
    field_name = None

    def get_field_object(self):
        if self.model is None:
            class_name = self.__class__.__name__
            raise ModelNotImplementedError(
                LazyFormat((f"{class_name} could not"
                f" retrieve the field object for '{self.field_name}'."))
            )

        return self.model._get_field_by_name(self.field_name)

    def resolve(self):
        raise NotImplementedError('Expression resolution should be implement by child classes')


class Math(ExpressionMixin):
    def __init__(self, value: Any, by: Union[int, float], 
                 days: int=None, month: int=None, year: int=None):
        self.value = value
        self.by = by
        self.days = days
        self.month = month
        self.year = year

    def __repr__(self):
        return f"{self.__class__.__name__}(field={self.field_name})"

    def resolve(self):
        field = self.get_field_object()
        field.resolve(self.value)
        return field
        

class Substract(Math):
    """
    Substracts an incoming value to another
    """
    def resolve(self):
        field = super().resolve()
        self._cached_data = field._cached_result - self.by
        return self._cached_data


class Add(Math):
    """
    Adds an incoming element to a value
    """
    def resolve(self):
        field = super().resolve()
        self._cached_data = field._cached_result + self.by
        return self._cached_data


class Multiply(Math):
    """
    Multiplies an incoming element to a value
    """

    def resolve(self):
        field = super().resolve()
        self._cached_data = field._cached_result * self.by
        return self._cached_data


class Divide(Math):
    """
    Divides the incoming value by another
    """

    def resolve(self):
        field = super().resolve()
        self._cached_data = field._cached_result / self.by
        return self._cached_data


class When:
    _cached_data = None
    model = None

    def __init__(self, if_condition, then_condition, else_condition=None):
        self.if_condition = if_condition
        self.then_condition = then_condition
        self.else_condition = else_condition

    def __repr__(self):
        template = "{class_name}({conditions})"
        conditions = f"THEN {self.then_condition}"
        if self.else_condition is not None:
            conditions = conditions + f" ELSE {self.else_condition}"
        return template.format(
            class_name=self.__class__.__name__,
            conditions=conditions
        )

    def resolve(self):
        field_name, exp, value_to_compare = self.parse_expression(self.if_condition)
        field_object = self.model._get_field_by_name(field_name)
        
        result = self.compare(exp, value_to_compare)
        if result:
            field_object.resolve(self.then_condition)
            return field_name, self.then_condition
        
        field_object.resolve(self.else_condition)
        return field_name, field_object._cached_result 

    def parse_expression(self, expression: str):
        allowed = ['gt', 'lt', 'lte', 'gte', 'eq', 'contains']
        
        try:
            field_name, rhs = expression.split('__', maxsplit=1)
        except ValueError:
            raise ValueError((f'Case requires a valid operator '
            'e.g. value__gt or value__eq.'))

        try:
            exp, value_to_compare = rhs.split('=', maxsplit=1)
        except ValueError:
            raise ValueError(f'Case requires a comparision value e.g. {field_name}__gt=??')

        if exp not in allowed:
            raise ValueError()

        return field_name, exp, value_to_compare

    def compare(self, exp, value) -> bool:
        result = False

        # If there's nothing in the
        # _cached_result attribute, just force 
        # the then/else condition directly
        if self._cached_data is None:
            return result

        # Detect if the value can
        # be an integer or a float and
        # if so get the true value
        value = string_to_number(value)

        # If the types that we are trying
        # to compare are not the same,
        # we should not run a comparision
        # otherwise this will raise a TypeError
        if type(value) != type(self._cached_data):
            template = ('Comparision is not support betweet {type1} and {type2}. ' 
                        'Make sure the data types of the value to compare are the '
                        'same when using the When-function.')
            message = LazyFormat(template, type1=type(value), type2=type(self._cached_data))
            raise TypeError(message)

        # TODO: Maybe if the value is a string,
        # calculate it's length and improve the
        # the comparision without raising a
        # useless error

        if exp == 'gt':
            result = self._cached_data > value

        if exp == 'lt':
            result = self._cached_data < value
        
        if exp == 'eq':
            result = self._cached_data == value
        
        if exp == 'gte':
            result = self._cached_data >= value
        
        if exp == 'lte':
            result = self._cached_data <= value

        if exp == 'contains':
            if isinstance(value, (int, float)):
                result = value == self._cached_data
            else:
                result = value in self._cached_data
        
        return result


class DateExtractorMixin:
    lookup_name = None
    field_name = None

    def __init__(self, value: Any, output_field: Callable=None, date_format: str=None):
        self.value = value
        self.date = None
        self.output_field = output_field
        self.date_format = date_format

    def resolve(self):
        from zineb.models.fields import DateField

        # IMPORTANT: In order to extract a year, a month
        # a day... from the incoming value, we logically 
        # should only get to deal with a DateField
        source_field = super().get_field_object()
        if not isinstance(source_field, DateField):
            raise TypeError(LazyFormat('{field} should be an instance of DateField.', field=source_field))

        if self.output_field is None:
            self.output_field = source_field

        source_field.date_formats.add(self.date_format)
        source_field.resolve(self.value)

        self._cached_data = source_field._cached_result
        result = getattr(self._cached_data, self.lookup_name)
        if isinstance(self.output_field, DateField):
            return result
        else:
            self.output_field._simple_resolve(result, convert=True)
            return self.output_field._cached_result


class ExtractYear(DateExtractorMixin, ExpressionMixin):
    lookup_name = 'year'


class ExtractMonth(DateExtractorMixin, ExpressionMixin):
    lookup_name = 'month'


class ExtractDay(DateExtractorMixin, ExpressionMixin):
    lookup_name = 'day'
