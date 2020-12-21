import re
from functools import wraps
from zineb.exceptions import ValidationError

def regex_compiler(pattern):
    def compiler(func):
        def wrapper(value):
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
def validate_email(email):
    if '@' not in email:
        raise ValidationError(f'{email} is not a valid email for the field')
    return email


def validate_is_not_null(value):
    if value is None:
        raise TypeError('None values are not permitted')
    if value == '':
        raise ValueError('Empty values are not permitted')
    return value


def validate_length(value, max_length):
    result = max_length_validator(len(value), max_length)
    if result:
        raise ValidationError('Ensure value is no more than', max_length)
    # return value


@regex_compiler(r'(?<=\.)(\w+)\Z')
def validate_extension(clean_value, extensions:list=[]):
    base_extensions = []
    base_extensions = base_extensions + extensions
    if clean_value not in base_extensions:
        raise ValidationError('Value is not a valid extension')
    return clean_value


def max_length_validator(a, b):
    return a > b


def min_length_validator(a, b):
    return a < b


@regex_compiler(r'^(\-?\d+[\W]\d?)(?=\%$)')
def validate_percentage(number):
    return number


def validate_url(url):
    return url
