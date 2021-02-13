import datetime
import re
import unittest

from zineb.exceptions import ValidationError
from zineb.models import fields
from zineb.models.fields import CharField, DecimalField


class TestBaseField(unittest.TestCase):
    def setUp(self):
        self.field = fields.Field()

    def test_resolution(self):
        result = self.field.resolve('   Kendall Jenner')
        self.assertEqual(result, 'Kendall Jenner')

        result = self.field.resolve(' \n \n Kendall \t Jenner ')
        self.assertEqual(result, 'Kendall Jenner')

    def test_max_length_respected(self):
        constrained_field = fields.Field(max_length=5)
        self.assertRaises(
            ValidationError, 
            constrained_field.resolve, 
            'Kendall Jenner'
        )

    def test_not_null_respected(self):
        constrained_field = fields.Field(null=False)
        self.assertRaises(
            (ValidationError, ValueError),
            constrained_field.resolve,
            ''
        )

    def test_none_is_returned_as_is(self):
        # Check that None is returned and does
        # not block the application IF there is
        # no constraint on null type
        self.assertIsNone(self.field.resolve(None))

    def test_get_default_instead_of_none(self):
        constrained_field = fields.Field(default='Hailey Baldwin')
        self.assertEqual(constrained_field.resolve(None), 'Hailey Baldwin')


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


class TestCharfields(unittest.TestCase):
    def setUp(self):
        self.charfield = fields.CharField()
        self.textfield = fields.TextField()
        self.namefield = fields.NameField()

    def test_resolution(self):
        text = 'I love Kendall Jenner'
        self.charfield.resolve(text)
        self.assertEqual(self.charfield._cached_result, text)

        self.textfield.resolve(text)
        self.assertEqual(self.textfield._cached_result, text)

        name = 'kendall jenner'
        self.namefield.resolve(name)
        self.assertEqual(self.namefield._cached_result, 'Kendall Jenner')


class TestEmailField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = fields.EmailField()

    def test_resolution(self):
        email = 'kendall.jenner@gmail.com'
        self.field.resolve(email)
        self.assertEqual(self.field._cached_result, email)


class TestIntegerField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = fields.IntegerField()

    def test_resolution(self):
        self.field.resolve('15')
        self.assertEqual(self.field._cached_result, 15)

        self.field.resolve(15)
        self.assertEqual(self.field._cached_result, 15)


class TestDateField(unittest.TestCase):
    def setUp(self) -> None:
        self.field = fields.DateField('%d/%m/%Y')
        self.agefield = fields.AgeField('%d/%m/%Y')

    def test_resolution(self):
        d = '15/06/2002'
        self.field.resolve(d)
        self.assertIsInstance(self.field._cached_result, datetime.datetime)
        self.assertEqual(str(self.field._cached_result.date()), '2002-06-15')
        self.assertEqual(str(self.field), '2002-06-15')

        age = self.agefield.resolve(d)
        self.assertEqual(str(self.field._cached_result.date()), '2002-06-15')
        self.assertEqual(str(self.agefield), '19')
        self.assertEqual(age, 19)


def method_one(value):
    return value + ' Kendall'

def method_two(value):
    return value + ' Jenner'


def method_three(price):
    is_match = re.search(r'^\$(\d+\.?\d+)$', price)
    if is_match:
        return is_match.group(1)
    return price


class TestFunctionField(unittest.TestCase):
    def setUp(self):
        self.field = fields.FunctionField(
            method_one, method_two
        )

    def test_resolution(self):
        self.field.resolve('I love')
        self.assertEqual(self.field._cached_result, 'I love Kendall Jenner')
        
    def test_output_field(self):
        field = fields.FunctionField(
            method_one, method_two, output_field=fields.CharField()
        )
        field.resolve('I love')
        self.assertEqual(field._cached_result, 'I love Kendall Jenner')

    def test_parsing_price(self):
        field = fields.FunctionField(
            method_three, output_field=DecimalField()
        )
        field.resolve('$456.7')
        self.assertEqual(field._cached_result, 456.7)

if __name__ == "__main__":
    unittest.main()
