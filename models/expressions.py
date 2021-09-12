from typing import Union
import datetime

from zineb.exceptions import ModelNotImplementedError
from zineb.utils.conversion import string_to_number
from zineb.utils.formatting import LazyFormat


class ExpressionMixin:
    _cached_data = None
    model = None

    def get_field_object(self):
        if self.model is None:
            raise ModelNotImplementedError((f"{self.__class__.__name__} could not"
            f" retrieve the field object for '{self.field_name}' - {self.__class__.__name__}.model is {self.model}"))

        field_object = self.model._get_field_by_name(self.field_name)
        field_object.resolve(self._cached_data)
        return field_object

    def resolve(self):
        raise NotImplementedError('Expression resoltion should be implement by child classes')


class Calculate(ExpressionMixin):
    def __init__(self, field_name: str, by: Union[int, float], days: int=None, month: int=None, year: int=None):
        self.field_name = field_name
        self.by = by
        self._calculated_result = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self._cached_data})"


class Substract(Calculate):
    """
    Substracts a value from the incoming element

    Parameters
    ----------

        Calculate ([type]): [description]
    """
    def resolve(self):
        field_object = self.get_field_object()
        self._calculated_result = field_object._cached_result - self.by
        field_object.resolve(self._calculated_result)


class Add(Calculate):
    """
    Adds a value to the incoming element

    Parameters
    ----------

        Calculate ([type]): [description]
    """
    def resolve(self):
        field_object = self.get_field_object()
        self._calculated_result = field_object._cached_result + self.by
        field_object.resolve(self._calculated_result)


class Multiply(Calculate):
    """
    Adds a value to the incoming element

    Parameters
    ----------

        Calculate ([type]): [description]
    """

    def resolve(self):
        field_object = self.get_field_object()
        self._calculated_result = field_object._cached_result * self.by
        field_object.resolve(self._calculated_result)


class Divide(Calculate):
    """
    Adds a value to the incoming element

    Parameters
    ----------

        Calculate ([type]): [description]
    """

    def resolve(self):
        field_object = self.get_field_object()
        self._calculated_result = field_object._cached_result / self.by
        field_object.resolve(self._calculated_result)


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


# class F:
#     _cached_data = None
#     model = None

#     def __init__(self, field: str):
#         self.field_name = field

#     def __repr__(self) -> str:
#         return f"{self.__class__.__name__}({self._cached_data})"

#     def __str__(self):
#         return self._cached_data

#     def __contains__(self, value):
#         if self._cached_data.isnumeric():
#             return self._cached_data == value
#         return value in self._cached_data

#     def __add__(self, value):
#         return self._cached_data + value

#     def __sub__(self, value):
#         return self._cached_data - value

#     def __div__(self, value):
#         return self._cached_data / value

#     def resolve(self):
#         field_object = self.model._get_field_by_name(self.field_name)


class PositionMixin:
    def __init__(self, field: str):
        self.field_name = field

    def get_field_cached_values(self):
        return self.model._cached_result.get(self.field_name)


class Last(PositionMixin, ExpressionMixin):
    def resolve(self):
        cached_values = self.get_field_cached_values()
        return cached_values[-1]


class First(PositionMixin, ExpressionMixin):
    def resolve(self):
        cached_values = self.get_field_cached_values()
        result = cached_values[:1]
        if result:
            return result[-1]
        return None


# class Latest:
#     pass


# class Earliest:
#     pass


class Min(PositionMixin, ExpressionMixin):
    def resolve(self):
        cached_values = self.get_field_cached_values()
        return min(cached_values)


class Max(Min):
    def resolve(self):
        cached_values = self.get_field_cached_values()
        return max(cached_values)



class DateExtractorMixin:
    def __init__(self, name: str):
        self.field_name = name

    def resolve(self, value):
        pass


class ExtractYear(DateExtractorMixin):
    pass


class ExtractMonth(DateExtractorMixin):
    pass


class ExtractDay(DateExtractorMixin):
    pass
