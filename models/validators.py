import re
from functools import wraps
from typing import Any, Callable, Tuple, Union

from w3lib.url import is_url
from zineb.exceptions import ValidationError


def regex_compiler(pattern: str):
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


@regex_compiler(r'^\w+\W?\w+@\w+\W\w+$')
def validate_email(email) -> str:
    if '@' not in email:
        raise ValidationError(f'{email} is not a valid email for the field')
    return email


def validate_is_not_null(value: Any):
    if value is None:
        raise TypeError('None values are not permitted')
    if value == '':
        raise ValueError('Empty values are not permitted')
    return value


def validate_length(value, max_length):
    result = max_length_validator(len(value), max_length)
    if result:
        raise ValidationError('Ensure value is no more than', max_length)
    return value


@regex_compiler(r'(?<=\.)(\w+)\Z')
def validate_extension(clean_value, extensions: list = []):
    base_extensions = []
    base_extensions = base_extensions + extensions
    if clean_value not in base_extensions:
        raise ValidationError('Value is not a valid extension')
    return clean_value


def max_length_validator(a, b) -> bool:
    return a > b


def min_length_validator(a, b) -> bool:
    return a < b


@regex_compiler(r'^(\-?\d+[\W]\d?)(?=\%$)')
def validate_percentage(number) -> Union[int, float]:
    return number


def validate_url(url: str):
    if url.startswith('/'):
        return url

    url_is_valid = is_url(url)
    if not url_is_valid:
        raise ValidationError(f"Url is not valid. Got: '{url}'")
    return url


class LengthValidator:
    error_message = {
        'length_error': "%(value)s does not respect the %(validator)s constraint"
    }

    def __init__(self, constraint):
        self.constraint = constraint

    def __call__(self, value_to_test):
        value_length = value_to_test
        if isinstance(value_to_test, str):
            value_length = self._get_string_length(value_length)
        return value_length

    @staticmethod
    def _get_string_length(value):
        return len(value)

    def should_return_result(self, value, state, expected):
        if state != expected:
            message = self.error_message['length_error']
            raise ValidationError(message %  {'value': value, 'validator': self.__class__.__name__})


class MinLengthValidator(LengthValidator):
    def __call__(self, value_to_test: Any):
        value_length = super().__call__(value_to_test)
        result = min_length_validator(value_length, self.constraint)
        super().should_return_result(value_length, result, True)
        return value_to_test


class MaxLengthValidator(LengthValidator):
    def __call__(self, value_to_test: Any):
        value_length = super().__call__(value_to_test)
        result = max_length_validator(value_length, self.constraint)
        super().should_return_result(value_length, result, False)
        return value_to_test
