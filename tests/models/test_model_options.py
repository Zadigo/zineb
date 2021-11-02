from typing import OrderedDict
import unittest

from zineb.models.datastructure import ModelOptions


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
        # self.options._add_options([('ordering', ['-c', 'a'])])
        self.assertDictEqual(self.options.cached_options, OrderedDict([('ordering', ['b', '-a'])]))


if __name__ == '__main__':
    unittest.main()
