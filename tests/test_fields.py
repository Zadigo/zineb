import datetime
import re
import unittest

from zineb.exceptions import ValidationError
from zineb.models import fields
from zineb.models.fields import (BooleanField, CharField, DecimalField,
                                 RegexField)
from zineb.tests import TEST_DATE_FORMATS


class TestField(unittest.TestCase):
    def setUp(self):
        self.field = fields.Field()

    def test_resolution(self):
        values_to_resolve = [
            '   Kendall Jenner',
            ' \n \n Kendall \t Jenner '
        ]
        for value in values_to_resolve:
            result = self.field.resolve(value)
            self.assertEqual(result, 'Kendall Jenner')
        
    def test_none_is_returned_as_is(self):
        # Check that None is returned and does
        # not block the application IF there is
        # no constraint on null type
        self.assertIsNone(self.field.resolve(None))

    @unittest.expectedFailure
    def test_max_length_respected(self):
        # Test that we cannot indeed add a value which length > 5
        constrained_field = fields.Field(max_length=5)
        self.assertRaises(ValidationError, constrained_field.resolve,  'Kendall Jenner')

    @unittest.expectedFailure
    def test_not_null_respected(self):
        constrained_field = fields.Field(null=False)
        constrained_field._meta_attributes['field_name'] = 'test_field'
        constrained_field.resolve('')
        self.assertRaises(ValueError)

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
    def test_validation_raises_error(self):
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


class TestIntegerField(unittest.TestCase):
    def setUp(self):
        self.number_field = fields.IntegerField()
        self.float_field = fields.DecimalField()

    def test_resolution(self):
        numbers = ['15', 15]
        for number in numbers:
            self.number_field.resolve(number)
            self.assertEqual(self.number_field._cached_result, 15)

    @unittest.expectedFailure
    def test_max_value_raises_error(self):
        field = fields.IntegerField(max_value=100)
        self.assertRaises(ValidationError, field.resolve, 101)

    @unittest.expectedFailure
    def test_min_value_raises_error(self):
        field = fields.IntegerField(min_value=90, max_value=100)
        self.assertRaises(ValidationError, field.resolve, 60)


class TestDateField(unittest.TestCase):
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
        dates = ['2002-06-15', '2002.06.15', '2002/06/15', '15.6.2002', '02.6.15']
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
        self.assertDictEqual(self.field._cached_result, {'a': 1, 'b': str(d)})

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


if __name__ == "__main__":
    unittest.main()
