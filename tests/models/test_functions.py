import unittest

from zineb.models import fields, functions
from zineb.tests.models import items


class TestMathOperations(unittest.TestCase):
    def setUp(self):
        self.model = items.SimpleModel()

    def _instantiate_function(self, klass):
        instance = klass(5)
        instance._cached_data = 202
        instance.field_name = 'height'
        instance.model = self.model
        instance.resolve()
        return instance._cached_data

    def test_addition(self):
        result = self._instantiate_function(functions.Add)
        self.assertEqual(result, 207)

    def test_substraction(self):
        result = self._instantiate_function(functions.Substract)
        self.assertEqual(result, 197)

    def test_multiplication(self):
        result = self._instantiate_function(functions.Multiply)
        self.assertEqual(result, 1010)

    def test_division(self):
        result = self._instantiate_function(functions.Divide)
        self.assertEqual(result, 40.4)

    # def test_with_string(self):
    #     # TODO: Allow addition on strings ??
    #     instance = functions.Add(3)
    #     instance._cached_data = 'Something'
    #     instance.model = self.model
    #     instance.field_name = 'name'
    #     instance.resolve()
    #     self.assertEqual(instance._cached_data, 'Something5')


class TestWhen(unittest.TestCase):
    def setUp(self):
        self.model = items.BareModel()
        instance = functions.When('age__gt=15', 20)
        instance._cached_data = 25
        instance.model = self.model
        self.instance = instance

    @unittest.expectedFailure
    def test_wrong_field_name(self):
        instance = functions.When('WRONG__gt=1', 1)
        instance._cached_data = 25
        instance.model = self.model
        instance.resolve()

    @unittest.expectedFailure
    def test_no_model(self):
        instance = functions.When('age__gt=1', 1)
        instance.resolve()

    @unittest.expectedFailure
    def test_wrong_expressions(self):
        instance = functions.When(
            'age__gt=21',
            'Facebook',
            else_condition='Google'
        )
        instance.model = self.model
        instance.resolve()

    def test_no_operator(self):
        instance = functions.When('age=1', 1)
        with self.assertRaises(ValueError):
            instance.resolve()

    def test_resolution(self):
        # if age > 15, 20 else 15
        field_name, result = self.instance.resolve()
        self.assertIsInstance(field_name, str)
        self.assertEqual(result, 20)

    # def test_can_add_case(self):
    #     # BUG: "Could not find a valid format for date '23' on field 'age'."
    #     from zineb.models.functions import When
    #     self.model.add_case(21, When('age__eq=21', 23))
    #     result = self.model._data_container.as_values()
    #     self.assertDictEqual(result, {'age': [23]})

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
                field_name, exp, value = self.instance.parse_expression(
                    expression)
                self.assertEqual(field_name, 'age')
                self.assertIn(
                    exp, ['gt', 'lt', 'eq', 'lte', 'gte', 'contains'])
                self.assertEqual(value, '15')


class TestExtractDates(unittest.TestCase):
    def setUp(self):
        self.model = items.CalculatedModel()

    @unittest.expectedFailure
    def test_field_should_not_be_a_datefield(self):
        model = items.AgeModel()
        model.add_value('age', functions.ExtractDay('11-1-2021'))

    def _instantiate_function(self, klass, value='1987-1-1'):
        instance = klass(value)
        instance.model = self.model
        instance.field_name = 'age'
        instance.resolve()
        return instance

    def test_day_resolution(self):
        instance = self._instantiate_function(functions.ExtractDay)
        self.assertEqual(instance._cached_data, 1)

    def test_year_resolution(self):
        instance = self._instantiate_function(functions.ExtractYear)
        self.assertEqual(instance._cached_data, 1987)

    def test_month_resolution(self):
        instance = self._instantiate_function(functions.ExtractMonth)
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


class TestComparision(unittest.TestCase):
    @unittest.expectedFailure
    def test_different_types_error(self):
        instance = functions.Greatest('15', 15)
        instance.resolve()

    def test_greatest(self):
        instance = functions.Greatest(15, 31, 24)
        instance.resolve()
        self.assertEqual(instance._cached_data, 31)

    def test_smallest(self):
        instance = functions.Smallest(15, 31, 24)
        instance.resolve()
        self.assertEqual(instance._cached_data, 15)


if __name__ == '__main__':
    unittest.main()
