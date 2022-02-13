import datetime
from typing import Any, Union

from zineb.settings import lazy_settings
from zineb.utils.conversion import string_to_number

import math
from typing import Any, Callable, Union

from zineb.exceptions import ModelNotImplementedError
from zineb.models.fields import Value
from zineb.utils.conversion import string_to_number
from zineb.utils.formatting import LazyFormat


class FunctionsMixin:
    _cached_data = None
    field_name = None
    model = None
    
    def _to_python_object(self, value):
        return value

    def get_field_object(self):
        try:
            return self.model._get_field_by_name(self.field_name)
        except:
            class_name = self.__class__.__name__
            text= "{class_name} could not retrieve the field object for '{field_name}'"
            raise ModelNotImplementedError(
                LazyFormat(text, class_name=class_name, field_name=self.field_name)
            )

    def resolve(self):
        raise NotImplementedError('Expression resolution should be implement by child classes')


class Math(FunctionsMixin):
    ADD = '+'
    SUBSTRACT = '-'
    DIVIDE = '/'
    MULTIPLY = '*'

    def __init__(self, by: Union[int, float]):
        self.by = by

    def __repr__(self):
        class_name = self.__class__.__name__
        
        if class_name == 'Add':
            result = f"{self._cached_data} {self.ADD} {self.by}"
        elif class_name == 'Substract':
            result = f"{self._cached_data} {self.SUBSTRACT} {self.by}"
        elif class_name == 'Divide':
            result = f"{self._cached_data} {self.DIVIDE} {self.by}"
        elif class_name == 'Multiply':
            result = f"{self._cached_data} {self.MULTIPLY} {self.by}"
        else:
            result = f"{self._cached_data} {self.by}"

        return f"{class_name}(< {result} >)"

    def resolve(self):
        source_field = self.get_field_object()

        if self._cached_data is None:
            raise ValueError(LazyFormat("{func} requires a value. Got: '{value}'",
            func=self.__class__.__name__, value=self._cached_data))

        source_field.resolve(self._cached_data)
        return source_field
        

class Substract(Math):
    """
    Substracts an incoming value to another
    """
    def resolve(self):
        source_field = super().resolve()
        self._cached_data = source_field._cached_result - self.by


class Add(Math):
    """
    Adds an incoming element to a value
    """
    def resolve(self):
        source_field = super().resolve()
        self._cached_data = source_field._cached_result + self.by


class Multiply(Math):
    """
    Multiplies an incoming element to a value
    """

    def resolve(self):
        source_field = super().resolve()
        self._cached_data = source_field._cached_result * self.by


class Divide(Math):
    """
    Divides the incoming value by another
    """

    def resolve(self):
        source_field = super().resolve()
        self._cached_data = source_field._cached_result / self.by

        
# class Mean(StatisticsMixin):
#     """
#     Returns the mean value from a list of
#     numerical values
#     """
    
#     def resolve(self):
#         values = super().resolve()
#         self._cached_data = sum(values) / len(values)        
#         return self._cached_data
    
    
# class StDev(StatisticsMixin):
#     """Returns the standard deviation of
#     a list of numerical values"""
    
#     @staticmethod
#     def calculate_variance(values, mean):
#         a = map(lambda x: math.pow(x - mean, 2), values)
#         return sum(a) / len(values)
    
#     def resolve(self):
#         values = super().resolve()
#         mean = sum(values) / len(values)
#         variance = self.calculate_variance(values, mean)
#         return math.sqrt(variance)
        

class When:
    """Returns a parsed value if a condition is
    respected otherwise, implements the default"""
    
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

    def __init__(self, value: Any, date_format: str=None):
        self.value = value
        self._datetime_object = None
        
        self.date_parser = datetime.datetime.strptime
        
        formats = set(getattr(lazy_settings, 'DEFAULT_DATE_FORMATS'))
        formats.add(date_format)
        self.date_formats = formats
        
    def _to_python_object(self, value):
        for date_format in self.date_formats:
            try:
                d = self.date_parser(value, date_format)
            except:
                d = None
            else:
                if d:
                    break

        if d is None:
            message = LazyFormat("Could not find a valid format for "
            "date '{d}' on field '{name}'.", d=value, name=self._meta_attributes.get('field_name'))
            raise ValueError(message)
        return d.date()

    def resolve(self):        
        self._datetime_object = self._to_python_object(self.value)
        self._cached_data = getattr(self._datetime_object, self.lookup_name)
                
        source_field = super().get_field_object()
        
        # TODO: Technically, it makes no sense to use
        # a date extractor on the DateField 
        from zineb.models.fields import DateField
        if isinstance(source_field, DateField):
            raise TypeError(LazyFormat("Cannot use {function} with DateField", function=self.__class__.__name__))
        
        # We have already resolved the date and for these
        # specific two fields, we want to implement the
        # resolved value without passing through the whole
        # resolution process of these field
        source_field._simple_resolve(self._cached_data)
        
        
class ExtractYear(DateExtractorMixin, FunctionsMixin):
    lookup_name = 'year'


class ExtractMonth(DateExtractorMixin, FunctionsMixin):
    lookup_name = 'month'


class ExtractDay(DateExtractorMixin, FunctionsMixin):
    lookup_name = 'day'


# class Truncate(FunctionsMixin):
#     def __init__(self, value: str, by: int):
#         self.initial_value = value
#         self.by = by
        
#     def resolve(self):
#         if not isinstance(self.initial_value, str):
#             raise ValueError()
        
#         self._cached_data = self.value[:self.by]


class ComparisionMixin(FunctionsMixin):
    def __init__(self, *values):
        values = list(values)
        types = []
        values_length = len(values)
        
        # Make sure that each value is of the same
        # type by comparing the previous one to the one
        # ahead of it. If one comparision fails,
        # does not matter, everything fails
        
        for value in values:
            types.append(type(value).__name__)
        
        results = []
        for i, name in enumerate(types):
            if i == values_length - 1:
                break
            results.append(name == types[i + 1])
            
        if not all(results):
            raise ValueError('All the values should be of the same type')
        self.values = values 
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.values})"


class Greatest(ComparisionMixin):
    """Takes a list of values and returns the greatest
    one. Each values should be of the same type"""
        
    def resolve(self):
        self._cached_data = max(self.values)
        
        
class Smallest(ComparisionMixin):
    """Takes a list of values and returns the smallest
    one. Each values should be of the same type"""
    
    def resolve(self):
        self._cached_data = min(self.values)


# class Replace(FunctionsMixin):
#     def __init__(self, value: Any, by: Any):
