import unittest

from zineb.models import functions
from zineb.models import fields
from zineb.tests.models import items


class TestMathOperations(unittest.TestCase):
    def setUp(self):
        self.model = items.BareModel()
    
    def test_addition(self):
        instance = functions.Add(5)
        instance._cached_data = 30
        instance.field_name = 'age'
        instance.model = self.model
        instance.resolve()
        self.assertEqual(instance._cached_data, 35)

    def test_substraction(self):
        instance = functions.Substract(5)
        instance._cached_data = 30
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 25)

    def test_multiplication(self):
        instance = functions.Multiply(2)
        instance._cached_data = 30
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 60)

    def test_division(self):
        instance = functions.Divide(2)
        instance._cached_data = 30
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 15)
        
    def test_can_add_values_of_two_different_types(self):
        # Even though the value is a string result
        # of the model field, ensure that we can
        # still add it to a number for example
        instance = functions.Add(5)
        instance.model = items.SimpleModel()
        instance.field_name = 'name'
        
        values_to_test = ['30', 'Kendall', 5]
        for value in values_to_test:
            with self.subTest(value=value):
                instance._cached_data = value
                instance.resolve()
                self.assertIn(instance._cached_data, ['305', 'Kendall5', '55'])
                
    def test_can_use_multiple_math_instances(self):
        model = items.BareModel()
        instances = [functions.Add(1), functions.Add(2)]
        for instance in instances:
            instance.model = model
            instance.field_name = 'age'
        model.add_calculated_value('age', 1, *instances)
        self.assertListEqual(model._cached_result.as_list(), [{'age': 4}])


class TestWhen(unittest.TestCase):
    def setUp(self):
        self.model = items.BareModel()
        instance = functions.When('age__gt=15', 20)
        instance._cached_data = 25
        instance.model = self.model
        self.instance = instance

    def test_resolution(self):
        # if age > 15, 20 else 15
        field_name, result = self.instance.resolve()
        self.assertIsInstance(field_name, str)
        self.assertEqual(result, 20)

    def test_comparision(self):
        result = self.instance.compare('gt', '10')
        self.assertTrue(result)

        result = self.instance.compare('lt', '15')
        self.assertFalse(result)

        result = self.instance.compare('contains', '15')
        self.assertFalse(result)

    def test_expression_parsing(self):
        expressions = [
            'age__gt=15',
            'age__lt=15',
            'age__eq=15',
            'age__lte=15',
            'age__gte=15',
            'age__contains=15'
        ]
        for expression in expressions:
            with self.subTest(expression=expression):
                field_name, exp, value = self.instance.parse_expression(expression)
                self.assertEqual(field_name, 'age')
                self.assertIn(exp, ['gt', 'lt', 'eq', 'lte', 'gte', 'contains'])
                self.assertEqual(value, '15')

    # def test_adding_to_model(self):
    #     self.model.add_case(15, self.instance)
    #     self.assertDictEqual(dict(self.model._cached_result.values), {'age': [(1, 30), (2, 15)]})

        # self.model.add_case(15, When('age__lt=20', 25, else_condition='age'))
        # self.assertDictEqual(self.model._cached_result, {'age': [15, 25]})


class TestExtractDates(unittest.TestCase):
    def setUp(self):
        self.model = items.CalculatedModel()

    def test_day_resolution(self):
        instance = functions.ExtractDay('1987-1-1')
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 1)

    def test_year_resolution(self):
        instance = functions.ExtractYear('1987-1-1')
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 1987)

    def test_month_resolution(self):
        instance = functions.ExtractMonth('1987-1-1')
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        self.assertEqual(instance._cached_data, 1)

    def test_can_extract_from_any_format(self):
        dates = ['1987-1-1', '1.1.1987', '1-1-1987', '1/1/1987', 
                'Oct 1, 1987', '1-1-02', '02-1-1', '1.1.02']
        for d in dates:
            with self.subTest(d=d):
                instance = functions.ExtractDay(d)
                instance.model = self.model
                instance.field_name = 'age'
                instance.resolve()
                self.assertEqual(instance._cached_data, 1)

    def test_can_extract_from_custom_format(self):
        dates = ['Oct 1 1987']
        for d in dates:
            with self.subTest(d=d):
                instance = functions.ExtractYear(d, date_format='%b %d %Y')
                instance.model = self.model
                instance.field_name = 'age'
                instance.resolve()
                self.assertEqual(instance._cached_data, 1987)

    # @unittest.expectedFailure
    def test_field_should_not_be_a_datefield(self):
        self.model._meta.cached_fields['age'] = fields.DateField()
        self.assertRaises(TypeError, self.model.add_value, name='age', value=functions.ExtractYear('11-1-2021'))


if __name__ == '__main__':
    unittest.main()
