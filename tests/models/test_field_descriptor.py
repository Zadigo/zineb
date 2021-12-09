import unittest
from typing import OrderedDict

from models.fields import CharField
from zineb.models import fields
from zineb.models.datastructure import FieldDescriptor


class TestFieldDescriptor(unittest.TestCase):
    def setUp(self):
        self.descriptor = FieldDescriptor()
        self.descriptor.cached_fields = OrderedDict([('name', fields.CharField())])
    
    def test_can_get_field(self):
        field = self.descriptor.get_field('name')
        self.assertIsInstance(field, CharField)

    def test_name_in_field(self):
        self.assertListEqual(self.descriptor.field_names, ['name'])

if __name__ == '__main__':
    unittest.main()
