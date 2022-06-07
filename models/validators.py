import re
from typing import Any, Callable, Tuple, Union

from zineb.exceptions import ValidationError
from zineb.utils.conversion import convert_if_number
from zineb.utils.formatting import LazyFormat
from zineb.utils.urls import is_url


class RegexValidator:
    def __init__(self, value):
        self.initial_value = value
        
    def __call__(self, pattern: str):
        compiled_pattern = re.compile(pattern)
        result = compiled_pattern.search(self.initial_value)
        if not result or result is None:
            raise ValidationError("Regex could not match pattern")
        return result.group()


def regex_compiler(pattern: str):
    """Regex decorator for model validators"""
    def compiler(func: Callable[[Tuple], Any]):
        def wrapper(value: Any, **kwargs):
            compiled_pattern = re.compile(pattern)
            result = compiled_pattern.match(str(value))
            if not result or result is None:
                raise ValidationError('The value is not valid')
            return func(result.group())
        return wrapper
    return compiler


@regex_compiler(r'^-?\d+$')
def validate_numeric(clean_value):
    if not clean_value.isnumeric():
        raise ValidationError('Value is not numeric')
    return clean_value

# TODO: The email validation pattern is quite limited,
# we are no looking for something complexe but just one
# that catch common mistakes in email addresses
@regex_compiler(r'^\w+\W?\w+@\w+\W\w+$')
def validate_email(email) -> str:
    if '@' not in email:
        raise ValidationError(f'{email} is not a valid email for the field')
    return email


def validate_is_not_null(value: Any):
    from zineb.models.fields import Empty

    message = ('{prefix} values are not '
    'permitted on this field')
    
    if value is None:
        raise TypeError(message.format(prefix='None'))
    
    if value == '' or value == Empty:
        raise ValueError(message.format(prefix='Empty'))
    return value


def validate_length(value, max_length):
    result = max_length_validator(len(value), max_length)
    if result:
        raise ValidationError('Ensure value is no more than', max_length)
    return value


# @regex_compiler(r'(?<=\.)(\w+)\Z')
# def validate_extension(clean_value, extensions: list=[]):
#     if clean_value not in extensions:
#         raise ValidationError('Value is not a valid extension')
#     return clean_value


def validate_extension(extensions: list = []):
    def validator(clean_value):
        regex_validator = RegexValidator(clean_value)
        result = regex_validator(r'(?<=\.)(\w{3,4})\Z')
        if result not in extensions:
            raise ValidationError(LazyFormat("'.{extension}' is not valid extension", extension=result))
        return clean_value
    return validator


def max_length_validator(a, b) -> bool:
    return a >= b


def min_length_validator(a, b) -> bool:
    return a <= b


@regex_compiler(r'^(\-?\d+[\W]\d?)(?=\%$)')
def validate_percentage(number) -> Union[int, float]:
    return number


def validate_url(url: str):
    if url.startswith('/'):
        return url

    url_is_valid = is_url(url)
    if not url_is_valid:
        raise ValidationError(("The following url failed the "
        f"validation test. Got: '{url}'"))
    return url


class LengthValidator:
    error_message = {
        'length_error': "'%(value)s' does not respect the %(validator)s constraint."
    }

    def __init__(self, constraint):
        self.constraint = constraint

    def __call__(self, value_to_test):
        # On this validator, values come
        # exclusively as a string but if
        # the string contains a number, we
        # need to get its true represention
        # in order for the comparision to
        # be valid
        if value_to_test.isnumeric():
            return convert_if_number(value_to_test)

        if isinstance(value_to_test, str):
            return self._get_string_length(value_to_test)
            
        return value_to_test

    @staticmethod
    def _get_string_length(value):
        return len(value)

    def should_return_result(self, value: Any, state: bool, expected: bool):
        """
        Based on an expected value, raise an error if the
        state is not equals to the expected one

        Parameters
        ----------

            - value (Any): value to test
            - state (bool): result of the comparision
            - expected (bool): expected result from the comparision
        """
        if state != expected:
            message = self.error_message['length_error']
            raise ValidationError(message %  {'value': value, 'validator': self.__class__.__name__})


class MinLengthValidator(LengthValidator):
    def __call__(self, value_to_test: Any):
        value_length = super().__call__(value_to_test)
        result = min_length_validator(value_length, self.constraint)
        super().should_return_result(value_length, result, False)
        return value_to_test


class MaxLengthValidator(LengthValidator):
    def __call__(self, value_to_test: Any):
        value_length = super().__call__(value_to_test)
        result = max_length_validator(value_length, self.constraint)
        super().should_return_result(value_length, result, False)
        return value_to_test
