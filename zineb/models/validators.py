import re

from zineb.exceptions import ValidationError
from zineb.utils.conversion import convert_if_number
from zineb.utils.formatting import LazyFormat
from zineb.utils.urls import is_url


class RegexValidator:
    def __init__(self, value):
        self.initial_value = value

    def __call__(self, pattern):
        compiled_pattern = re.compile(pattern)
        result = compiled_pattern.search(self.initial_value)
        if not result or result is None:
            raise ValidationError("Regex could not match pattern")
        return result.group()


def regex_compiler(pattern):
    """Regex decorator for creating validators
    that require regex validation

    >>> @regex_compiler(r'\w+')
    ... def my_validator(clean_value):
    ...     # Do something here
    """
    def compiler(func):
        def wrapper(value, **kwargs):
            compiled_pattern = re.compile(pattern)
            result = compiled_pattern.match(str(value))

            if not result or result is None:
                raise ValidationError('The value is not valid')

            func(result.group())
        return wrapper
    return compiler


@regex_compiler(r'^-?\d+$')
def validate_numeric(clean_value):
    if not clean_value.isnumeric():
        raise ValidationError('Value is not numeric')


# TODO: The email validation pattern is quite limited,
# we are no looking for something complexe but just one
# that catch common mistakes in email addresses
@regex_compiler(r'^\w+\W?\w+@\w+\W\w+$')
def validate_email(email) -> str:
    if '@' not in email:
        raise ValidationError(f'{email} is not a valid email for the field')


def validate_is_not_null(value):
    from zineb.models.fields import Empty

    message = '{prefix} values are not permitted on this field'
    errors = []

    if value is None:
        errors.append(ValueError(message.format(prefix='None')))

    if value == '' or value == Empty:
        errors.append(ValueError(message.format(prefix="'' or Empty")))

    if errors:
        raise ExceptionGroup('Not null validation fail', errors)


def validate_length(value, max_length):
    result = max_length_validator(len(value), max_length)
    if result:
        raise ValidationError(
            f'Ensure value is no more than {max_length} long')


def validate_extension(extensions=[]):
    def validator(clean_value):
        regex_validator = RegexValidator(clean_value)
        result = regex_validator(r'(?<=\.)(\w+)\Z')
        if result not in extensions:
            raise ValidationError(LazyFormat(
                "'.{extension}' is not valid extension", extension=result))
    return validator


def max_length_validator(a, b):
    return a >= b


def min_length_validator(a, b):
    return a <= b


def validate_percentage(value):
    regex_compiler = RegexValidator(value)
    regex_compiler(r'^(?:\-?)(\d+\.?\d+)\%$')


def validate_url(url):
    if not url.startswith('/'):
        url_is_valid = is_url(url)
        if not url_is_valid:
            raise ValidationError(("The following url failed the "
                               f"validation test. Got: '{url}'"))


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
            return len(value_to_test)

        return value_to_test

    def should_return_result(self, value, state, expected):
        """
        Based on an expected value, raise an error if the
        state (which is `boolean`) is not equal to the expected one
        (which is also a `boolean`)

        >>> result = max_length(20, 15)
        ... instance.should_return_result(20, result, True)
        ... ValidationError(...)
        """
        if state != expected:
            message = self.error_message['length_error']
            raise ValidationError(
                message % {'value': value, 'validator': self.__class__.__name__})


class MinLengthValidator(LengthValidator):
    def __call__(self, value_to_test):
        value_length = super().__call__(value_to_test)
        result = min_length_validator(value_length, self.constraint)
        super().should_return_result(value_length, result, False)


class MaxLengthValidator(LengthValidator):
    def __call__(self, value_to_test):
        value_length = super().__call__(value_to_test)
        result = max_length_validator(value_length, self.constraint)
        super().should_return_result(value_length, result, False)
