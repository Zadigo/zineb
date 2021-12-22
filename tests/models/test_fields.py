import datetime
import re
import unittest
from unittest.case import TestCase, expectedFailure

from zineb.exceptions import ValidationError
from zineb.models import fields
from zineb.models.fields import (BooleanField, CharField, DecimalField,
                                 RegexField, Value)


class TestField(unittest.TestCase):
    def setUp(self):
        self.field = fields.Field()

    def test_resolution(self):
        # TODO: Put more values to test
        values_to_resolve = [
            '   Kendall Jenner',
            ' \n \n Kendall \t Jenner ',
            '<a>Kendall Jenner',
            '<a>Kendall Jenner</a>'
        ]
        for value in values_to_resolve:
            with self.subTest(value=value):
                self.field.resolve(value)
                self.assertEqual(self.field._cached_result, 'Kendall Jenner')
        
    def test_none_is_returned_as_is(self):
        # Check that None is returned and does
        # not block the application IF there is
        # no constraint on null type
        self.field.resolve(None)
        self.assertIsNone(self.field._cached_result)

    @unittest.expectedFailure
    def test_max_length_respected(self):
        # Test that we cannot indeed add a value which length > 5
        constrained_field = fields.Field(max_length=5)
        self.assertRaises(ValidationError, constrained_field.resolve,  'Kendall Jenner')

    @unittest.expectedFailure
    def test_not_null_respected(self):
        constrained_field = fields.Field(null=False)
        constrained_field._meta_attributes['field_name'] = 'test_field'
        self.assertRaises(ValueError, constrained_field.resolve, '')

    def test_get_default_instead_of_none(self):
        constrained_field = fields.Field(default='Hailey Baldwin')
        constrained_field.resolve(None)
        self.assertEqual(constrained_field._cached_result, 'Hailey Baldwin')

        constrained_field.resolve('Kendall Jenner')
        self.assertEqual(constrained_field._cached_result, 'Kendall Jenner')

    def test_run_validators(self):
        def test_validator(value):
            return value

        def test_validator_2(value):
            return f"{value} Kardashian"

        self.field._validators = [test_validator, test_validator_2]
        result = self.field._run_validation('Kendall Jenner')
        self.assertEqual(result, 'Kendall Jenner Kardashian')
        
    @unittest.expectedFailure
    def test_validation_raises_error(self):
        def raising_validator(value):
            if value == 'Kendall':
                raise ValidationError('Value is not good')
            return value
        self.field._default_validators = [raising_validator]
        self.assertRaises(ValidationError, self.field.resolve, 'Kendall')
        

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
        names = [
            'kendall jenner',
            'kendall Jenner',
            'Kendall Jenner'
        ]
        for name in names:
            self.namefield.resolve(name)
            self.assertEqual(self.namefield._cached_result, 'Kendall Jenner')


class TestEmailField(unittest.TestCase):
    def setUp(self):
        self.field = fields.EmailField()

    def test_field_resolution(self):
        email = 'kendall.jenner@gmail.com'
        self.field.resolve(email)
        self.assertEqual(self.field._cached_result, email)
        
    def test_email_in_limit_domains(self):
        field = fields.EmailField(limit_to_domains=['outlook.com'])
        self.assertRaises(ValidationError, field.resolve, 'kendall.jenner@gmail.com')


class TestIntegerField(unittest.TestCase):
    def setUp(self):
        self.field = fields.IntegerField()

    def test_resolution(self):
        numbers = ['15', 15]
        for number in numbers:
            with self.subTest(number=number):
                self.field.resolve(number)
                self.assertEqual(self.field._cached_result, 15)

    @unittest.expectedFailure
    def test_max_value_raises_error(self):
        field = fields.IntegerField(max_value=100)
        self.assertRaises(ValidationError, field.resolve, 101)

    @unittest.expectedFailure
    def test_min_value_raises_error(self):
        field = fields.IntegerField(min_value=90, max_value=100)
        self.assertRaises(ValidationError, field.resolve, 60)


class TestDecimalField(TestCase):
    def setUp(self) -> None:
        self.field = fields.DecimalField()
        
    def test_resolution(self):
        values_to_test = ['1.5', 1.5]
        for value in values_to_test:
            with self.subTest(value=value):
                self.field.resolve(value)
                self.assertEqual(self.field._cached_result, 1.5)
                self.assertIsInstance(self.field._cached_result, float)


class TestDateFields(unittest.TestCase):
    def setUp(self) -> None:
        self.d = '15/06/2002'
        
        self.field = fields.DateField()
        self.agefield = fields.AgeField()

        self.field.resolve(self.d)

    def test_date_resolution(self):
        # self.assertIsInstance(self.field._cached_result, datetime.datetime.date)
        self.assertEqual(str(self.field._cached_result), '2002-06-15')
    
    def test_age_resolution(self):
        # Test basic age resolution with builtin formats
        dates = ['2002-06-15', '2002.06.15', '2002/06/15', '15.6.2002']
        for date in dates:
            self.agefield.resolve(date)
            # Make sure that incoming dates respect the Y-m-d format
            self.assertEqual(str(self.agefield._cached_date), '2002-06-15')
            # Age should be 19 regardless of format
            self.assertEqual(self.agefield._cached_result, 19)

    def test_age_resolution_with_custom_format(self):
        agefield = fields.AgeField('%b %d, %Y')
        agefield.resolve('Oct 15, 2002')
        self.assertEqual(agefield._cached_result, 19)



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
        # Each function should be run sequentially
        # the result, building upon one another
        self.field.resolve('I love')
        self.assertEqual(self.field._cached_result, 'I love Kendall Jenner')
        
    def test_with_output_field(self):
        methods = [method_one, method_two]
        field = fields.FunctionField(*methods, output_field=fields.CharField())
        field.resolve('I love')
        self.assertEqual(field._cached_result, 'I love Kendall Jenner')

    @unittest.expectedFailure
    def test_with_none_instanciated_output_field(self):
        methods = [method_one, method_two]
        field = fields.FunctionField(*methods, output_field=fields.CharField)
        field.resolve('I love')
        self.assertEqual(field._cached_result, 'I love Kendall Jenner')

    def test_special_resolution(self):
        field = fields.FunctionField(method_three, output_field=DecimalField())
        field.resolve('$456.7')
        self.assertEqual(field._cached_result, 456.7)


class TestListField(unittest.TestCase):
    def setUp(self):
        self.field = fields.ListField()

    def test_resolution(self):
        values_to_test = [[1, 2, 3], '[1, 2, 3]']
        for value in values_to_test:
            with self.subTest(value=value):
                self.field.resolve(value)
                self.assertIsInstance(self.field._cached_result, list)
                self.assertListEqual(self.field._cached_result, [1, 2, 3])


class TestCommaSeparatedField(unittest.TestCase):
    def setUp(self):
        self.field = fields.CommaSeperatedField()

    def test_resolution(self):
        values_to_test = [[1, 2, 3], '[1, 2, 3]']
        for value in values_to_test:
            with self.subTest(value=value):
                self.field.resolve([1, 2, 3])
                self.assertEqual(self.field._cached_result, '1,2,3')
                
    # def test_special_resolution(self):
    #     value = "1,a,4,3,fast-fashion,hoohle@gmail.com,goole1__intelligent,hoodieislife,ùùei><,<>"
    #     self.field.resolve(value)
    #     self.assertEqual(self.field._cached_result, value)


class TestUrlField(unittest.TestCase):
    def setUp(self):
        self.field = fields.URLField()
        
    def test_resolution(self):
        values_to_test = [
            'http://example.com',
            'https://example.com'
        ]
        for value in values_to_test:
            with self.subTest(value=value):
                self.field.resolve(value)
                self.assertIn(self.field._cached_result, [
                    'http://example.com','https://example.com',
                    'ftp://example.com', 'http://example.com/',
                    'https://example.com/'
                ])
    
    def test_invalid_urls(self):
        values_to_test = [
            'ftp://example.com',
            'example.com'
        ]
        for value in values_to_test:
            with self.subTest(value=value):
                self.assertRaises(Exception, self.field.resolve, value)


class TestImageField(unittest.TestCase):
    def setUp(self):
        self.field = fields.ImageField()
    
    def test_resolution(self):
        values_to_test = ['http://example.com']
        for value in values_to_test:
            with self.subTest(value=value):
                self.field.resolve(value)
                self.assertIn(self.field._cached_result, ['http://example.com', 'http://example.com/'])


class TestBooleanField(unittest.TestCase):
    def setUp(self):
        self.field = BooleanField()

    def test_resolution(self):
        booleans = ['True', 'true', True, 'on', 'On', 'off', 'Off', 'False', 'false', False, 0, 1, '0', 1]
        for boolean in booleans:
            self.field.resolve(boolean)
            self.assertIsInstance(self.field._cached_result, bool)

    def test_true_values_should_be_true(self):
        trues = ['True', 'true', True, 'on', 'On', 1, '1']
        for item in trues:
            self.field.resolve(item)
            self.assertTrue(self.field._cached_result)
    
    def test_false_values_should_be_false(self):
        trues = ['off', 'Off', 'False', 'false', False, 0, '0']
        for item in trues:
            self.field.resolve(item)
            self.assertFalse(self.field._cached_result)


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
        self.assertDictEqual(self.field._cached_result, {'a': 1, 'b': d})

        self.field.resolve("<a>{'a': 1}</a>")
        self.assertDictEqual(self.field._cached_result, {'a': 1})


class TestRegexField(unittest.TestCase):
    def setUp(self):
        self.field = RegexField(r'wing\s?spiker')
    
    def test_resolution(self):
        values = [
            'she is a wing spiker',
            '\nwing spiker',
            '  wing spiker'
            'wingspiker',
            'wing     spiker'
        ]
        for value in values:
            self.field.resolve(value)
            self.assertEqual(self.field._cached_result, 'wing spiker')


class TestValueField(TestCase):
    def test_resolution(self):
        values_to_test = [' Kendall ', '<Kendall', '<div>Kendall</', 
                  '<div>Kendall</div>', '>>Kendall']
        
        for value in values_to_test:
            with self.subTest(value=value):
                instance = Value(value)
                self.assertEqual(instance.result, 'Kendall')


if __name__ == "__main__":
    unittest.main()
