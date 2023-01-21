"""
Models are a simple way to store and output data that
was scrapped from the internet. They are composed of three
main items:

    - Fields: which main purpose is to clean, normalize the incoming values
    
    - Internal container: which stores the incoming data
    
    - Model class: which is the central point for organizing all these elements to work together
"""

import datetime
import unittest

from zineb.exceptions import ModelExistsError, ValidationError
from zineb.models import fields
from zineb.models.datastructure import ModelOptions, model_registry
from zineb.models.functions import ExtractYear, Substract, When
from zineb.tests.models import items


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = items.SimpleModel()

    @unittest.expectedFailure
    def test_wrong_value_to_field(self):
        # Should not be able to add a value that
        # is not the correct format to a field
        self.model.add_value('age', 176)
        with self.assertRaises(ValidationError):
            print('Test cannot add wrong value to field')

    @unittest.expectedFailure
    def test_field_does_not_exist(self):
        self.model.add_value('FIELD_DOES_NOT_EXIST', None)

    def test_can_add_simple_value_to_model(self):
        self.model.add_value('date_of_birth', '1-1-2002')
        self.assertIsInstance(self.model._data_container.as_values(), dict)
        expected_result = {
            'age': [None],
            'id': [],
            'date_of_birth': ['2002-01-01'],
            'name': [None]
        }
        self.assertDictEqual(
            dict(self.model._data_container.as_values()), expected_result)

    def test_can_add_value_via_iteration(self):
        for i in range(4):
            self.model.add_value('name', f'Kendall{i}')

        expected_result = {
            'id': [],
            'age': [None, None, None, None],
            'date_of_birth': [None, None, None, None],
            'name': ['Kendall0', 'Kendall1', 'Kendall2', 'Kendall3']
        }
        self.assertDictEqual(
            dict(self.model._data_container.as_values()), expected_result)

    def test_model_result_within_a_loop(self):
        # The model should normally return the last value
        # of the iteration if the user instanciates the model
        # repeteadly in a loop since this would be the normal
        # behaviour for adding values
        for i in range(1, 4):
            model = items.SimpleModel()
            model.add_value('name', f'Kendall{i}')

        expected_result = {
            'id': [],
            'age': [None],
            'date_of_birth': [None],
            'name': ['Kendall3']
        }
        self.assertDictEqual(
            dict(model._data_container.as_values()), expected_result)

    def test_row_balancing(self):
        # Even when we add a value to only one of the
        # declared fields, we should get a balanced row
        self.model.add_value('date_of_birth', '1-1-2002')

        result = dict(self.model._data_container.as_values())
        for key, values in result.items():
            with self.subTest(key=key):
                if key != 'id':
                    self.assertEqual(len(values), 1)

    def test_fields_are_registered(self):
        # Access the registered fields on the model
        self.assertIsInstance(self.model._meta, ModelOptions)
        expected_fields = ['age', 'date_of_birth', 'name']

        for name in expected_fields:
            with self.subTest(name=name):
                self.assertIn(name, self.model._meta.field_names)

    def test_global_field_registration_on_model(self):
        self.assertIsInstance(
            self.model._get_field_by_name('name'),
            fields.CharField
        )
        self.assertIsInstance(
            self.model._meta.get_field('date_of_birth'),
            fields.DateField
        )
        self.assertIsInstance(
            self.model._meta.fields_map['age'],
            fields.AgeField
        )

    def test_instanciated_meta(self):
        self.assertIsInstance(self.model._meta, ModelOptions)
        self.assertIsInstance(self.model._meta.get_field('name'), fields.Field)
        self.assertEqual(self.model._meta.model_name, 'simplemodel')
        self.assertIsNotNone(self.model._meta.model)

    def test_deferred_attribute_result(self):
        # When calling model.field_name on the
        # model instance, we should get the data
        # container for that field
        self.model.add_value('name', 'Kendall')
        self.assertListEqual(self.model.name, ['Kendall'])

    def test_save(self):
        self.model.add_value('name', 'Kendall')
        self.model.add_value('age', '1992-01-24')
        self.model.add_value('date_of_birth', '1992-01-24')
        result = self.model.save(commit=False)

        self.assertGreater(len(result), 0)
        self.assertIsInstance(result, list)
        current_age = datetime.datetime.now().year - 1992
        expected_result = [
            {
                'age': current_age,
                'date_of_birth': '1992-01-24',
                'name': 'Kendall'
            }
        ]

        self.assertListEqual(result, expected_result)
        for item in result:
            with self.subTest(item=item):
                self.assertIsInstance(item, dict)
                self.assertTrue('name' in item)
                self.assertTrue('age' in item)
                self.assertTrue('date_of_birth' in item)

    # def test_can_add_using_expression(self):
    #     model = SimpleModel(html_document=None)
    #     model.add_using_expression('age', 'span', attrs={'id': 'age'})
    #     self.assertDictEqual(model._data_container, {'age': 23})



    def test_adding_types_of_different_values(self):
        model = items.ComplicatedModel()

        model.add_value('name', 'Kendall Jenner')
        model.add_value('year_of_birth', ExtractYear('1992-10-4'))
        model.add_case(59000, When('zip_code__eq=59000', 59))
        model.add_calculated_value('current_balance', 15000, Substract(5000))

        result = model.save(commit=False)
        expected_result = [
            {
                'name': 'Kendall Jenner',
                'year_of_birth': 1992,
                'zip_code': 59,
                'current_balance': 10000
            }
        ]
        self.assertListEqual(result, expected_result)

    def test_sorting(self):
        model = items.ModelWithMeta()
        model.add_value('name', 'Kendall')
        model.add_value('name', 'Candice')
        result = model.save(commit=False)
        expected = [{'name': 'Candice'}, {'name': 'Kendall'}]
        self.assertListEqual(result, expected)

    def test_relationships(self):
        # 1. We should be able to get the related
        # model as an instance: forward relationship
        model = items.RelatedModel1()
        model.add_value('age', 24)
        self.assertIsInstance(model.surname, items.RelatedModel2)

        # 2. We should be able to add values to the
        # related model
        model.surname.add_value('surname', 'Kendall')
        self.assertListEqual(
            model.surname._data_container.as_list(),
            [{'surname': 'Kendall'}]
        )

        # 3. The final result should be the result of the
        # main model data with the result of the related
        # model data nested in the data of the main model
        # e.g. [{...: ..., ...: {...}}]
        result = model.save(commit=False)
        self.assertListEqual(
            result,
            [{'age': 24, 'surname': [{'surname': 'Kendall'}]}]
        )

        # We SHOULD NOT be able to add values
        # to a RelatedModel field directly on
        # on main model e.g. model.add_value('name', 'Kendall')
        # but through model.name.add_value(...)

    # def test_add_two_different_models(self):
    #     model1 = test_models.ModelToAdd1()
    #     model2 = test_models.ModelToAdd2()

    #     new_model = model1 + model2


class TestModelWithValidators(unittest.TestCase):
    def setUp(self):
        self.model = items.ModelWithValidator()

    @unittest.expectedFailure
    def test_field_with_validation_error(self):
        self.model.add_value('weight', 0)

    def test_field_with_validation(self):
        self.model.add_value('height', 156)
        self.assertDictEqual(
            self.model._data_container.as_values(),
            {
                'weight': [None],
                'height': [156],
                'id': []
            }
        )


class TestModelRegistery(unittest.TestCase):
    def test_registry_has_model(self):
        model = model_registry['SimpleModel']
        self.assertIsNotNone(model)

    def test_can_get_all_models(self):
        self.assertGreater(len(model_registry.models), 0)

    @unittest.expectedFailure
    def test_adding_existing_model(self):
        model_registry.add('SimpleModel', items.SimpleModel)
        with self.assertRaises(ModelExistsError):
            print('Model exists')


if __name__ == '__main__':
    unittest.main()
