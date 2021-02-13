from zineb.models import validators
import unittest
from zineb.models import fields

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


if __name__ == "__main__":
    unittest.main()
