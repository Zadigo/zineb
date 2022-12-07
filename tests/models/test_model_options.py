import inspect
import unittest

from zineb.models import fields
from zineb.models.datastructure import ModelOptions
from zineb.tests.models.test_models import items


class TestModelOptions(unittest.TestCase):
    def setUp(self):
        self.model = items.SimpleModel()
             
    def test_class_integrity(self):
        self.assertIsInstance(self.model._meta, ModelOptions)
        self.assertTrue(inspect.isclass(self.model._meta.model))
        self.assertEqual(self.model._meta.model_name, 'simplemodel')
        self.assertTrue(len(self.model._meta.fields_map) > 0)
        self.assertFalse(self.model._meta.has_ordering)
        self.assertTrue(self.model._meta.has_field('id'))
        self.assertIsInstance(self.model._meta.get_field('id'), fields.AutoField)
        self.assertListEqual(self.model._meta.field_names, ['age', 'date_of_birth', 'id', 'name'])
        
        # Fields
        self.assertIsNotNone(self.model._meta.get_field('name'))
        self.assertIsInstance(self.model._meta.get_field('name'), fields.Field)

    def test_model_ordering(self):
        model = items.ModelWithInvalidMeta()
        ordering = model._meta.get_ordering()
        self.assertListEqual(ordering.ascending_fields, ['name'])
        self.assertListEqual(ordering.booleans, [('name', False)])
        
    @unittest.expectedFailure
    def test_cannot_add_existing_field(self):
        self.model._meta.add_field('name', fields.BooleanField())


if __name__ == '__main__':
    unittest.main()
