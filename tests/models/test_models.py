import unittest

from zineb.exceptions import FieldError, ModelExistsError, ValidationError
from zineb.models import fields
from zineb.models.datastructure import Model, ModelOptions, model_registry
from zineb.models.functions import (Add, Divide, ExtractDay, ExtractMonth,
                                    ExtractYear, Multiply, Substract, When)
from zineb.tests.models.items import (BareModel, CalculatedModel, DateModel,
                                      ModelWithMeta, ModelWithValidator,
                                      SimpleModel, ComplicatedModel)


class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = SimpleModel()

    def test_can_add_value(self):
        self.model.add_value('date_of_birth', '1-1-2002')
        self.assertDictEqual(self.model._data_container.as_values(), {'age': [None], 'date_of_birth': ['2002-01-01'], 'name': [None]})

    def test_model_in_iteration(self):
        for i in range(1, 4):
            self.model.add_value('name', f'Kendall{i}')
            
        expected = {
            'age': [None, None, None], 
            'date_of_birth': [None, None, None], 
            'name': ['Kendall1', 'Kendall2', 'Kendall3']
        }
        self.assertDictEqual(self.model._data_container.as_values(), expected)

    def test_model_instanciation_in_iteration(self):
        # The model should return the last value of
        # iteration if the user instanciates the model
        # repeteadly in a loop
        for i in range(1, 4):
            model = SimpleModel()
            model.add_value('name', f'Kendall{i}')
        expected = {
            'age': [None],
            'date_of_birth': [None],
            'name': ['Kendall3']
        }
        self.assertDictEqual(model._data_container.as_values(), expected)

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

    def test_row_balancing(self):
        # Even when we add values to one of the x
        # other fields, we should get a balanced row
        self.model.add_value('date_of_birth', '1-1-2002')
        self.model.full_clean()
        self.assertListEqual(self.model._cached_resolved_data, [
                             {'age': None, 'date_of_birth': '2002-01-01', 'name': None}])

    def test_field_names(self):
        # Access the registered fields on the model
        self.assertIsInstance(self.model._meta, ModelOptions)
        for name in ['age', 'date_of_birth', 'name']:
            with self.subTest(name=name):
                self.assertIn(name, self.model._meta.field_names)

    def test_can_get_field(self):
        self.assertIsInstance(self.model._get_field_by_name('name'), fields.CharField)
        self.assertIsInstance(self.model._meta.get_field('date_of_birth'), fields.DateField)
        self.assertIsInstance(self.model._meta.fields_map['age'], fields.AgeField)
        
    def test_instanciated_meta(self):
        self.assertIsInstance(self.model._meta, ModelOptions)
        self.assertIsInstance(self.model._meta.get_field('name'), fields.Field)
        self.assertEqual(self.model._meta.model_name, 'simplemodel')
        self.assertIsNotNone(self.model._meta.model)
        
    def test_deferred_attribute(self):
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
        expected = [{'age': 30, 'date_of_birth': '1992-01-24', 'name': 'Kendall'}]
        
        self.assertListEqual(result, expected)
        for item in result:
            with self.subTest(item=item):
                self.assertIsInstance(item, dict)
                self.assertTrue('name' in item)
                self.assertTrue('age' in item)
                self.assertTrue('date_of_birth' in item)
                
    def test_adding_values(self):
        model = ComplicatedModel()
        model.add_value('name', 'Kendall Jenner')
        model.add_value('year_of_birth', ExtractYear('1992-10-4'))
        model.add_case(59000, When('zip_code__eq=59000', 59))
        model.add_calculated_value('current_balance', 15000, Substract(5000))
        result = model.save(commit=False)
        expected = [{'name': 'Kendall Jenner', 'year_of_birth': 1992, 'zip_code': 59, 'current_balance': 10000}]
        self.assertListEqual(result, expected)
        
    def test_sorting(self):
        model = ModelWithMeta()
        model.add_value('name', 'Kendall')
        model.add_value('name', 'Candice')
        result = model.save(commit=False)
        expected = [{'name': 'Candice'}, {'name': 'Kendall'}]
        self.assertListEqual(result, expected)
        
class TestModelWithValidators(unittest.TestCase):
    def setUp(self):
        self.model = ModelWithValidator()

    def test_field_with_validation(self):
        self.model.add_value('height', 156)
        self.assertDictEqual(self.model._data_container.as_values(), {'height': [156]})
        
    






# class TestModelRegistery(unittest.TestCase):
#     def test_has_model(self):
#         result = model_registry.has_model('SimpleModel')
#         self.assertTrue(result)

#     def test_can_get_model(self):
#         model = model_registry.get_model('SimpleModel')
#         self.assertIsInstance(model, SimpleModel)

#     def test_can_get_all_models(self):
#         self.assertGreater(len(model_registry.models), 0)

#     def test_can_iterate(self):
#         for model in model_registry:
#             with self.subTest(model=model):
#                 self.assertTrue(issubclass(model, Model))

#     @unittest.expectedFailure
#     def test_adding_existing_model(self):
#         model_registry.add('SimpleModel', SimpleModel)
#         with self.assertRaises(ModelExistsError):
#             pass


# class TestModelWithOptions(unittest.TestCase):
#     def test_options(self):
#         pass
    # def test_can_add_case(self):
    #     model.add_case(21, When('age__eq=21', 23))
    #     self.assertDictEqual(model._data_container, {'age': [23]})

    # def test_can_add_using_expression(self):
    #     model = SimpleModel(html_document=None)
    #     model.add_using_expression('age', 'span', attrs={'id': 'age'})
    #     self.assertDictEqual(model._data_container, {'age': 23})

    # def test_add_related_value(self):
    #     model.add_related_value('age', 'date_of_birth', '01-01-1992')
    #     # TODO: When adding a value to the fields, this can create
    #     # an unbalance between all fields and we should watch against that
    #     self.assertDictEqual(model._data_container, {
    #                          'date_of_birth': ['01-01-1992'], 'age': [23]})


# class TestModelForCalculation(unittest.TestCase):
#     def setUp(self):
#         self.model = CalculatedModel()

#     def test_can_add_calculated_value(self):
#         self.model.add_calculated_value('age', 17, Add(2))
#         self.assertDictEqual(self.model._data_container.as_values(), {'age': [19]})

#     def test_can_add_multiple_calculated_functions(self):
#         self.model.add_calculated_value('age', 17, Add(2), Substract(1))
#         self.assertDictEqual(self.model._data_container.as_values(), {'age': [18]})

#     def test_with_when(self):
#         self.model.add_case(21, When('age__gt=20', 18))
#         self.assertDictEqual(self.model._data_container.as_values(), {'age': [18]})
        
#     def test_using_function_with_add_value(self):
#         # Using a function that require calculation
#         # with a method other than add_calculated_value 
#         # should not be tolerated
#         self.assertRaises(ValueError, self.model.add_value, name='age', value=Add(3))
        

if __name__ == '__main__':
    unittest.main()
