import unittest
from unittest.case import TestCase

from zineb.exceptions import ValidationError
from zineb.models import fields, validators


def my_custom_validator(value):
    if value == 'Kendall Jenner':
        raise ValueError("Do not implement Kendall Jenner")
    return value

class WithBaseField(unittest.TestCase):
    def setUp(self):
        _validators = [
            my_custom_validator
        ]
        self.field = fields.Field(validators=_validators)

    def test_resolution(self):
        value = 'Kendall Jenner'
        with self.assertRaises(ValueError) as e:
            self.field.resolve(value)


def is_not_kendall_jenner(value):
    if value == 'Kendall Jenner':
        raise ValidationError('This field is not valid')
    return value


class MyCustomField(fields.Field):
    _default_validators = [is_not_kendall_jenner]


class TestGlobalValidators(unittest.TestCase):
    def setUp(self):
        self.field = MyCustomField()

    @unittest.expectedFailure
    def test_global_validation(self):
        self.field.resolve('Kendall Jenner')


class TestValidators(TestCase):
    def test_validate_numeric(self):
        value = validators.validate_numeric('1')
        self.assertIsInstance(value, str)

        value = validators.validate_numeric('-1')
        self.assertIsInstance(value, str)

    @unittest.expectedFailure
    def test_value_is_null(self):
        with self.assertRaises(TypeError):
            print('Value is None')

if __name__ == "__main__":
    unittest.main()
