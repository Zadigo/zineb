import datetime
from models.fields import RegexField
import re
import unittest

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
        self.assertRaises(ValidationError, constrained_field.resolve,  'Kendall Jenner')

    @unittest.expectedFailure
    def test_not_null_respected(self):
        constrained_field = fields.Field(null=False)
        constrained_field._meta_attributes['field_name'] = 'test_field'
        constrained_field.resolve('')
        self.assertRaises(ValueError)

    def test_none_is_returned_as_is(self):
        # Check that None is returned and does
        # not block the application IF there is
        # no constraint on null type
        self.assertIsNone(self.field.resolve(None))

    def test_get_default_instead_of_none(self):
        constrained_field = fields.Field(default='Hailey Baldwin')
        self.assertEqual(constrained_field.resolve(None), 'Hailey Baldwin')

        result = constrained_field.resolve('Kendall Jenner')
        self.assertEqual(result, 'Kendall Jenner')

    def test_run_validators(self):
        def test_validator(value):
            return value

        def test_validator_2(value):
            return f"{value} Kardashian"

        self.field._validators = [test_validator, test_validator_2]
        result = self.field._run_validation('Kendall Jenner')
        self.assertEqual(result, 'Kendall Jenner Kardashian')


def custom_validator(value):
    if value == 'Kendall':
        return value + ' Jenner'
    return value


def custom_validator_2(value):
    if value == 'Kendall Jenner':
        raise ValidationError(f'{value} is not permitted')


class TestFieldValidation(unittest.TestCase):
    def setUp(self):
        self.field = fields.CharField(validators=[custom_validator])
        self.invalid_field = fields.CharField(validators=[custom_validator_2])

    def test_custom_validation(self):
        self.field.resolve('Kendall')
        self.assertEqual(self.field._cached_result, 'Kendall Jenner')

    @unittest.expectedFailure
    def test_raises_error(self):
        self.assertRaises(ValidationError, self.invalid_field.resolve, 'Kendall Jenner')




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
    def setUp(self):
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

    @unittest.expectedFailure
    def test_max_value(self):
        field = fields.IntegerField(max_value=100)
        self.assertRaises(ValidationError, field.resolve, 101)

    @unittest.expectedFailure
    def test_min_value(self):
        field = fields.IntegerField(min_value=90, max_value=100)
        self.assertRaises(ValidationError, field.resolve, 60)


class TestDateField(unittest.TestCase):
    def setUp(self) -> None:
        self.d = '15/06/2002'
        
        self.field = fields.DateField()
        self.agefield = fields.AgeField()

        self.field.resolve(self.d)
        self.agefield.resolve(self.d)

    def test_date_resolution(self):
        # self.assertIsInstance(self.field._cached_result, datetime.datetime.date)
        self.assertEqual(str(self.field._cached_result), '2002-06-15')
    
    def test_age_resolution(self):
        self.assertEqual(str(self.agefield._cached_date), '2002-06-15')
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
        self.field = fields.FunctionField(method_one, method_two)

    def test_resolution(self):
        self.field.resolve('I love')
        self.assertEqual(self.field._cached_result, 'I love Kendall Jenner')
        
    def test_output_field(self):
        methods = [method_one, method_two]
        field = fields.FunctionField(*methods, output_field=fields.CharField())
        field.resolve('I love')
        self.assertEqual(field._cached_result, 'I love Kendall Jenner')

    def test_with_parsing_price(self):
        field = fields.FunctionField(method_three, output_field=DecimalField())
        field.resolve('$456.7')
        self.assertEqual(field._cached_result, 456.7)


class TestListField(unittest.TestCase):
    def setUp(self):
        self.field = fields.ListField()

    def test_resolution(self):
        self.field.resolve([1, 2, 3])
        self.assertIsInstance(self.field._cached_result, list)

        result = self.field.resolve('[1, 2]')
        self.assertListEqual(self.field._cached_result, [1, 2])


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
        field = fields.JsonField()
        field._meta_attributes['field_name'] = 'test_field'
        self.field = field

    def test_resolution_with_string(self):
        self.field.resolve("{'a': 1}")
        self.assertDictEqual(self.field._cached_result, {'a': 1})

        d = datetime.datetime.now().date()
        self.field.resolve({'a': 1, 'b': d})
        self.assertDictEqual(self.field._cached_result, {'a': 1, 'b': str(d)})

        self.field.resolve("<a>{'a': 1}</a>")
        self.assertDictEqual(self.field._cached_result, {'a': 1})


class TestRegexField(unittest.TestCase):
    def setUp(self):
        self.field = RegexField(r'wing\s?spiker')
    
    def test_resolution(self):
        self.field.resolve('she is a wing spiker')
        self.assertEqual(self.field._cached_result, 'wing spiker')


if __name__ == "__main__":
    unittest.main()
