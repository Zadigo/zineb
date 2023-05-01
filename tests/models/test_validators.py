import unittest
from unittest.case import TestCase

from zineb.exceptions import ValidationError
from zineb.models import fields, validators


class TestValidators(TestCase):
    def test_regex_validator(self):
        validator = validators.RegexValidator('Kendall Jenner')
        validator(r'^Kendall\s?')

    def test_validate_numeric(self):
        validators.validate_numeric(15)
        with self.assertRaises(ValidationError):
            validators.validate_numeric('google')

    def test_validate_email(self):
        validators.validate_email('example@gmail.com')

    def test_validate_is_not_null(self):
        validators.validate_is_not_null('Google')
        with self.assertRaises(ExceptionGroup):
            validators.validate_is_not_null(None)

    def test_validate_length(self):
        validators.validate_length('Kendall Jenner', 20)
        with self.assertRaises(ValidationError):
            validators.validate_length('Kendall Jenner', 5)

    def test_validate_extension(self):
        validator = validators.validate_extension(extensions=['jpg'])
        validator('http://example.com/image.jpg')

        with self.assertRaises(ValidationError):
            validator('image.pdf')

    def test_max_length_validator(self):
        validators.max_length_validator(5, 1)

    def test_min_length_validator(self):
        validators.max_length_validator(1, 5)

    def test_validate_percentage(self):
        validators.validate_percentage('10%')
        validators.validate_percentage('10.56%')
        validators.validate_percentage('-10.56%')

    def test_validate_url(self):
        validators.validate_url('http://example.com')
        validators.validate_url('/example.com')

    def test_length_validator_class(self):
        validator = validators.MinLengthValidator(2)
        validator('This is a text')

        validator = validators.MaxLengthValidator(2)
        with self.assertRaises(ValidationError):
            validator('This is a text')


def my_custom_validator(value):
    if value == 'Kendall Jenner':
        raise ValueError('Do not implement Kendall Jenner')


class WithBaseField(unittest.TestCase):
    def setUp(self):
        custom_validators = [my_custom_validator]
        self.field = fields.Field(validators=custom_validators)

    @unittest.expectedFailure
    def test_resolution_that_raises_error(self):
        value = 'Kendall Jenner'
        self.assertRaises(self.field.resolve, value=value)


def is_not_kendall_jenner(value):
    if value == 'Kendall Jenner':
        raise ValidationError('This field is not valid')


class MyCustomField(fields.Field):
    _default_validators = [is_not_kendall_jenner]


class TestCustomFieldValidation(unittest.TestCase):
    def setUp(self):
        self.field = MyCustomField()

    @unittest.expectedFailure
    def test_global_validation(self):
        self.field.resolve('Kendall Jenner')


if __name__ == '__main__':
    unittest.main()
