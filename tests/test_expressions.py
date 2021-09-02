import unittest

from zineb.models import expressions
from zineb.models.datastructure import Model
from zineb.models.expressions import When
from zineb.models.fields import AgeField, IntegerField


class TestModel(Model):
    age = IntegerField()


class TestCalculate(unittest.TestCase):
    def setUp(self):
        self.model = TestModel()
    
    def test_addition(self):
        instance = expressions.Add('age', 5)
        instance.model = self.model

        instance._cached_data = 15
        instance.resolve()
        self.assertEqual(instance._calculated_result, 20)

    def test_substraction(self):
        instance = expressions.Substract('age', 5)
        instance.model = self.model

        instance._cached_data = 15
        instance.resolve()
        self.assertEqual(instance._calculated_result, 10)

    def test_multiplication(self):
        instance = expressions.Multiply('age', 2)
        instance.model = self.model

        instance._cached_data = 15
        instance.resolve()
        self.assertEqual(instance._calculated_result, 30)


class TestWhen(unittest.TestCase):
    def setUp(self):
        self.model = TestModel()
        instance = expressions.When('age__gt=15', 20, else_condition=15)
        # Value that was originally
        # retrived from the HTML page
        instance._cached_result = 15

        instance.model = self.model
        self.instance = instance

    def test_resolution(self):
        # if age > 15, 20 else 15
        name, result = self.instance.resolve()
        self.assertIsInstance(name, str)
        self.assertEqual(result, 15)

    def test_comparision(self):
        result = self.instance.compare('gt', 10)
        self.assertTrue(result)

        result = self.instance.compare('lt', 15)
        self.assertFalse(result)

        result = self.instance.compare('contains', 15)
        self.assertTrue(result)

    def test_expression_parsing(self):
        field_name, exp, value = self.instance.parse_expression('age__gt=15')
        self.assertEqual(exp, 'gt')
        self.assertEqual(value, 15)
        self.assertEqual(field_name, 'age')

    def test_adding_to_model(self):
        self.model.add_case(15, self.instance)
        self.assertDictEqual(self.model._cached_result, {'age': [15]})

        self.model.add_case(15, When('age__lt=20', 25, else_condition='age'))
        self.assertDictEqual(self.model._cached_result, {'age': [15, 25]})


if __name__ == '__main__':
    unittest.main()
