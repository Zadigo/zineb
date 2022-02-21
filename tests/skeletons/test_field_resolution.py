"""
This is the base skeleton for Field resolution for the
framework. The field called calls the resolve function
in the superclass, runs validations and returns the value
"""

import unittest

from zineb.models.fields import Empty
from zineb.utils.conversion import convert_to_type


def test_validator(value):
    return value


class Field:
    _default_validators = [test_validator]
    _cached_result = None
    _dtype = str

    def __init__(self, default=None, validators=[]):
        self._default_validators.extend(validators)
        self.default = default
        
    def _true_or_default_value(self, value):
        if value is None and self.default is not None:
            return self.default
        elif value == Empty and self.default is not None:
            return self.default
        else:
            return value
    
    def _to_python_object(self, value, use_dtype=None):
        dtype = use_dtype or self._dtype
        return convert_to_type(value, dtype)

    def _run_validators(self, value):
        value = self._true_or_default_value(value)
        
        return_value = None
        for validator in self._default_validators:
            if return_value is None:
                return_value = validator(value)
            else:
                return_value = validator(return_value)
        # if not self._default_validators:
        #     return return_value
        # return value
        return return_value or value
    
    def _check_emptiness(self, value):
        if value == '':
            return Empty
        return value
    
    def _simple_resolve(self, value):
        if value == Empty or value is None:
            self._cached_result = self._run_validators(value)
        else: 
            result = self._to_python_object(value)
            self._cached_result = self._run_validators(result)

    def _simple_resolve(self, value):
        if value == Empty or value is None:
            self._cached_result = self._run_validators(value)
        else:
            result = self._to_python_object(value)
            self._cached_result = self._run_validators(result)

    def resolve(self, value):
        value_or_empty = self._check_emptiness(value)
        self._simple_resolve(value_or_empty)
        

class CharField(Field):
    def resolve(self, value):
        super().resolve(value)

c = CharField(default='Something')
c.resolve('')
c.resolve(None)
c.resolve('Kendall')
# c.resolve({'a': 1})
# c.resolve([1, 2])
# c.resolve('[1, 2]')
# c.resolve("{'a': 1}")

# class TestProcess(unittest.TestCase):
#     def test_returns_the_same_value(self):
#         self.assertEqual(c.resolve(15), 15)

# if __name__ == '__main__':
#     unittest.main()
