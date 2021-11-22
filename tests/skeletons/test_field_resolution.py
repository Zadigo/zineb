"""
This is the base skeleton for Field resolution for the
framework. The field called calls the resolve function
in the superclass, runs validations and returns the value
"""

import unittest


def test_validator(value):
    return value


class Field:
    _default_validators = [test_validator]

    def __init__(self, validators=[]):
        self._default_validators.extend(validators)

    def _run_validators(self, value):
        return_value = None
        for validator in self._default_validators:
            if return_value is None:
                return_value = validator(value)
            else:
                return_value = validator(return_value)
        if not self._default_validators:
            return return_value
        return value

    def resolve(self, value):
        return value
        

class CharField(Field):
    def resolve(self, value):
        return super().resolve(value)

# c = CharField()

class TestProcess(unittest.TestCase):
    def test_returns_the_same_value(self):
        self.assertEqual(c.resolve(15), 15)

if __name__ == '__main__':
    unittest.main()
