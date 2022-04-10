import unittest
from typing import OrderedDict

from zineb.models.datastructure import ModelOptions
from zineb.models.fields import CharField, NameField

OPTIONS = [
    ('ordering', ['b', '-a'])
]


class TestModelOptions(unittest.TestCase):
    def setUp(self):
        self.options = ModelOptions(OPTIONS)

    def test_ordering_options(self):
        self.assertListEqual(self.options.ordering_booleans, [True, False])
        self.assertEqual(self.options.ordering_field_names, {'b', 'a'})
        self.assertTrue(self.options.has_option('ordering'))

    def test_can_update_and_return_updated(self):
        self.assertDictEqual(self.options.cached_options, OrderedDict([('ordering', ['b', '-a'])]))
        
    def test_fields_mixin(self):
        fields = {
            'name': NameField(),
            'surname': CharField()
        }
        self.options.cached_fields = fields
        self.assertTrue(self.options.has_fields('name', 'surname'))
        self.assertListEqual(self.options.field_names, ['name', 'surname'])
        self.assertIsInstance(self.options.get_field('name'), CharField)


if __name__ == '__main__':
    unittest.main()
