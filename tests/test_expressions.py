from datetime import datetime
import unittest

from zineb.models import expressions
from zineb.models.datastructure import Model
from zineb.models.expressions import (DateExtractorMixin, ExtractMonth,
                                      ExtractYear, When)
from zineb.models.fields import AgeField, DateField, IntegerField
from zineb.tests._utils import test_model


class TestCalculate(unittest.TestCase):
    def setUp(self):
        self.model = test_model
    
    def test_addition(self):
        instance = expressions.Add(35, 5)
        instance.field_name = 'age'
        instance.model = self.model
        instance.resolve()
        self.assertEqual(instance._cached_data, 40)

    def test_substraction(self):
        instance = expressions.Substract(35, 5)
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 30)

    def test_multiplication(self):
        instance = expressions.Multiply(35, 2)
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 70)

    def test_division(self):
        instance = expressions.Divide(30, 2)
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 15)

    def test_can_add_calculated_value(self):
        self.model.add_value('age', expressions.Add(25, 5))
        self.assertEqual(self.model._cached_result.get_container('age'), [(1, 30)])

    # def test_with_string(self):
    #     # TODO: Allow addition on strings ??
    #     instance = expressions.Add('Something', 5)
    #     self.assertEqual(instance._cached_data, 'Something5')


class TestWhen(unittest.TestCase):
    def setUp(self):
        self.model = test_model
        instance = expressions.When('age__gt=15', 20, else_condition=15)

        # Value that was originally
        # retrived from the HTML page
        instance._cached_data = 25
        instance.model = self.model

        self.instance = instance

    def test_resolution(self):
        # if age > 15, 20 else 15
        field_name, result = self.instance.resolve()
        self.assertIsInstance(field_name, str)
        self.assertEqual(result, 20)

    @unittest.expectedFailure
    def test_cannot_compare_in_when(self):
        self.model.add_case('google', When('age__eq=21', 23))
        self.assertRaises(TypeError)

    def test_wrong_expression_in_when(self):
        instance = expressions.When('fast', 0, else_condition=0)
        self.assertRaises(TypeError)

    def test_comparision(self):
        result = self.instance.compare('gt', '10')
        self.assertTrue(result)

        result = self.instance.compare('lt', '15')
        self.assertFalse(result)

        result = self.instance.compare('contains', '15')
        self.assertFalse(result)

    def test_expression_parsing(self):
        field_name, exp, value = self.instance.parse_expression('age__gt=15')
        self.assertEqual(field_name, 'age')
        self.assertEqual(exp, 'gt')
        self.assertEqual(value, '15')

    def test_adding_to_model(self):
        self.model.add_case(15, self.instance)
        self.assertDictEqual(dict(self.model._cached_result.values), {'age': [(1, 30), (2, 15)]})

        # self.model.add_case(15, When('age__lt=20', 25, else_condition='age'))
        # self.assertDictEqual(self.model._cached_result, {'age': [15, 25]})


class SampleModel(Model):
    age = DateField()

class TestExtractDates(unittest.TestCase):
    def setUp(self):
        self.model = SampleModel()

    def test_can_extract_year(self):
        self.model.add_value('age', ExtractYear('11-1-1987'))
        self.assertListEqual(self.model._cached_result.get_container('age'), [1987])

    def test_can_extract_month(self):
        self.model.add_value('age', ExtractMonth('11-1-1987'))
        self.assertListEqual(self.model._cached_result.get_container('age'), [1])

    def test_can_extract_day(self):
        self.model.add_value('age', ExtractMonth('11-1-1987'))
        self.assertListEqual(self.model._cached_result.get_container('age'), [11])

    def test_global_resolution(self):
        mixin = DateExtractorMixin('11-1-2002')
        mixin.resolve()
        self.assertIsInstance(mixin._cached_data, datetime.datetime.date)

    @unittest.expectedFailure
    def test_field_should_be_a_datefield(self):
        source_field = self.model._fields.cached_fields['age'] = IntegerField()
        self.model.add_value('age', ExtractYear('11-1-2021'))
        self.assertRaises(TypeError)


if __name__ == '__main__':
    unittest.main()
