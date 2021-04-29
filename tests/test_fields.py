import datetime
import re
import unittest
from unittest.case import expectedFailure

import pandas

from zineb.exceptions import ValidationError
from zineb.models import fields
from zineb.models.fields import CharField, DecimalField

class TestField(unittest.TestCase):
    def setUp(self):
        self.field = fields.Field()

    def test_resolution(self):
        result = self.field.resolve('   Kendall Jenner')
        self.assertEqual(result, 'Kendall Jenner')

        result = self.field.resolve(' \n \n Kendall \t Jenner ')
        self.assertEqual(result, 'Kendall Jenner')

    @unittest.expectedFailure
    def test_max_length_respected(self):
        constrained_field = fields.Field(max_length=5)
        self.assertRaises(
            ValidationError, 
            constrained_field.resolve, 
            'Kendall Jenner'
        )

    def test_not_null_respected(self):
        constrained_field = fields.Field(null=False)
        with self.assertRaises((ValidationError, ValueError)):
            constrained_field.resolve('')

    def test_none_is_returned_as_is(self):
        # Check that None is returned and does
        # not block the application IF there is
        # no constraint on null type
        self.assertIsNone(self.field.resolve(None))

    def test_get_default_instead_of_none(self):
        constrained_field = fields.Field(default='Hailey Baldwin')
        self.assertEqual(constrained_field.resolve(None), 'Hailey Baldwin')


def custom_validator(value):
    if value == 'Kendall':
        return value + ' Jenner'
    return value

def custom_validation2(value):
    if value == 'Kendall Jenner':
        raise ValidationError(f'{value} is not permitted')


class TestFieldValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.field = fields.CharField(validators=[custom_validator])

    def test_custom_validation(self):
        self.field.resolve('Kendall')
        self.assertEqual(self.field._cached_result, 'Kendall Jenner')

    @unittest.expectedFailure
    def test_raises_error(self):
        self.assertRaises(ValidationError, self.field.resolve, 'Kendall Jenner')


class TestCharfields(unittest.TestCase):
    def setUp(self):
        self.charfield = fields.CharField()
        self.textfield = fields.TextField()
        self.namefield = fields.NameField()

    def test_charfield_resolution(self):
        text = 'I love Kendall Jenner'
        self.charfield.resolve(text)
        self.assertEqual(self.charfield._cached_result, text)

    def test_text_field_resolution(self):
        text = """
        Lorem Ipsum is simply dummy text of the printing and typesetting industry. 
        Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, 
        when an unknown printer took a galley of type and scrambled it to make a type 
        specimen book.
        """
        self.textfield.resolve(text)
        self.assertIn('Lorem Ipsum', self.textfield._cached_result)

    def test_name_field_resolution(self):
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
    def setUp(self):
        self.number_field = fields.IntegerField()
        self.float_field = fields.DecimalField()

    def test_resolution(self):
        self.number_field.resolve('15')
        self.assertEqual(self.number_field._cached_result, 15)

        self.number_field.resolve(15)
        self.assertEqual(self.number_field._cached_result, 15)

    @expectedFailure
    def test_max_value(self):
        field = fields.IntegerField(max_value=100)
        self.assertRaises(ValidationError, field.resolve, 101)


class TestDateField(unittest.TestCase):
    def setUp(self) -> None:
        self.d = '15/06/2002'
        self.field = fields.DateField('%d/%m/%Y')
        self.agefield = fields.AgeField('%d/%m/%Y')

    def test_date_resolution(self):
        self.field.resolve(self.d)
        self.assertIsInstance(self.field._cached_result, datetime.datetime)
        self.assertEqual(str(self.field._cached_result.date()), '2002-06-15')
        self.assertEqual(str(self.field), '2002-06-15')
    
    def test_age_resolution(self):
        self.agefield.resolve(self.d)
        self.assertEqual(str(self.agefield._cached_date.date()), '2002-06-15')
        self.assertEqual(self.agefield._cached_result, 19)



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


class TestArrayField(unittest.TestCase):
    def setUp(self):
        self.field = fields.ArrayField()

    def test_resolution(self):
        result = self.field.resolve([1, 2, 3])
        self.assertIsInstance(result, pandas.Series)

        result = self.field.resolve('[1, 2]')
        self.assertListEqual(pandas.Series([1, 2]).to_list(), result.to_list())


class TestCommaSeparatedField(unittest.TestCase):
    def setUp(self):
        self.field = fields.CommaSeperatedField()

    def test_resolution(self):
        self.field.resolve([1, 2, 3])
        self.assertEqual(self.field._cached_result, '1,2,3')



class TestUrlField(unittest.TestCase):
    pass


class TestImageField(unittest.TestCase):
    pass


class TestJsonField(unittest.TestCase):
    def setUp(self):
        self.field = fields.JsonField()

    def test_resolution(self):
        self.field.resolve("{'a': 1}")
        self.assertDictEqual(self.field._cached_result, {"a": 1})


if __name__ == "__main__":
    unittest.main()
