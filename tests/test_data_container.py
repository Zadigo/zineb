import unittest
from zineb.models.datastructure import DataContainer

class TestDataContainer(unittest.TestCase):
    def setUp(self):
        fields = ['name', 'age']
        self.container = DataContainer.as_container(*fields)

    def test_can_update_field(self):
        self.container.update('name', 'Kendall')
        self.assertDictEqual(dict(self.container.values), {'age': [(1, None)], 'name': [(1, 'Kendall')]})

    def test_final_container(self):
        result = self.container.as_values()
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()
