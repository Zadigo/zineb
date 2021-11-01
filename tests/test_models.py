import unittest

from zineb.exceptions import FieldError, ModelExistsError
from zineb.models.datastructure import (FieldDescriptor, Model, ModelOptions,
                                        model_registry)
from zineb.models.functions import (Add, Divide, ExtractDay, ExtractMonth,
                                    ExtractYear, Multiply, Substract, When)
from zineb.tests.models import ModelWithValidator, SimpleModel

from models import fields

model = SimpleModel()

class TestModelMeta(unittest.TestCase):
    def test_fields_descriptor(self):
        # Access the registered fields on the model
        self.assertIsInstance(model._fields, FieldDescriptor)
        self.assertListEqual(model._fields.field_names, ['name', 'age'])

    def test_meta(self):
        self.assertIsInstance(model._meta, ModelOptions)

    def test_can_get_field(self):
        self.assertIsInstance(model._get_field_by_name('name'), fields.CharField)
        self.assertIsInstance(model._fields.get_field('name'), fields.CharField)
        self.assertIsInstance(model._fields['name'], fields.CharField)


class TestSimpleModel(unittest.TestCase):
    def test_can_add_value_without_resolution(self):
        model._add_without_field_resolution('name', 'Kendall')
        self.assertDictEqual(model._cached_result, {'name': ['Kendall']})

    def test_can_add_value(self):
        model.add_value('age', 15)
        self.assertDictEqual(model._cached_result, {'age': [15]})

    def test_can_add_calculated_value(self):
        model.add_calculated_value(21, Add('age', 2))
        self.assertDictEqual(model._cached_result, {'age': [23]})

    def test_can_add_case(self):
        model.add_case(21, When('age__eq=21', 23))
        self.assertDictEqual(model._cached_result, {'age': [23]})

    def test_can_add_using_expression(self):
        model = SimpleModel(html_document=None)
        model.add_using_expression('age', 'span', attrs={'id': 'age'})
        self.assertDictEqual(model._cached_result, {'age': 23})

    def test_add_related_value(self):
        model.add_related_value('age', 'date_of_birth', '01-01-1992')
        # TODO: When adding a value to the fields, this can create
        # an unbalance between all fields and we should watch against that
        self.assertDictEqual(model._cached_result, {'date_of_birth': ['01-01-1992'], 'age': [23]})

    # def test_resolve_fields(self):
    #     df = model.resolve_fields()
    #     self.assertIsInstance(df, pandas.DataFrame)

    def test_can_clean(self):
        pass

    def test_can_save(self):
        pass

    def test_model_in_iteration(self):
        for i in range(1, 4):
            model.add_value('age', 15 + i)
        self.assertListEqual(model._cached_result, {'age': [15, 16, 17]})
        
    def test_model_instanciation_in_iteration(self):
        for i in range(1, 4):
            model = SimpleModel()
            model.add_value('age', 15 + i)
        self.assertListEqual(model._cached_result, {'age': [15, 16, 17]})

    def test_can_get_item(self):
        self.assertIsInstance(model['age'], (int, str, float))

    def test_ordering(self):
        pass

    def test_field_with_validation(self):
        model.add_value('height', 156)
        self.assertDictEqual(model._cached_result, {'height': [156]})

    @unittest.expectedFailure
    def test_wrong_value_to_field(self):
        model.add_value('height', 'Some height')
        with self.assertRaises(ValueError):
            pass

    @unittest.expectedFailure
    def test_field_does_not_exist(self):
        model.add_value('no_field', None)
        with self.assertRaises(FieldError):
            pass

    def test_data_container_unbalanced(self):
        model.add_value('age', 15)
        model.add_value('height', 202)
        # Technically, this should raise
        # an error when trying to resolve
        # the fields to a dataframe.
        
        # Expected: {name: [None], date_of_birth: [None], age: [15], height: [202]}
        model.resolve_fields()


class TestModelRegistery(unittest.TestCase):
    def test_has_model(self):
        result = model_registry.has_model('SimpleModel')
        self.assertTrue(result)

    def test_can_get_model(self):
        model = model_registry.get_model('SimpleModel')
        self.assertIsInstance(model, SimpleModel)

    def test_can_get_all_models(self):
        self.assertTrue(len(model_registry.models) > 0)

    def test_can_iterate(self):
        for model in model_registry:
            self.assertIsInstance(model, Model)

    @unittest.expectedFailure
    def test_adding_existing_model(self):
        model_registry.add('SimpleModel', SimpleModel)
        with self.assertRaises(ModelExistsError):
            print('Model exists.')



class ModelWithMeta(Model):
    name = fields.CharField()

    class Meta:
        ordering = ['name']


class TestModelWithOptions(unittest.TestCase):
    def test_options(self):
        pass


if __name__ == '__main__':
    unittest.main()
