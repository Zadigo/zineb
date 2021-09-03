import unittest
from zineb.models.datastructure import DataContainers

class TestDataContainer(unittest.TestCase):
    def setUp(self):
        fields = ['name', 'age']
        self.container = DataContainers.as_container(*fields)

    def test_can_update_field(self):
        self.container.update('name', 'Kendall')
        self.assertDictEqual(dict(self.container.values), {'age': [(1, None)], 'name': [(1, 'Kendall')]})

        

    # def test_can_finalize(self):
    #     self.container.values = []
    #     self.container.update('name', 'Kendall')
    #     result = self.container.finalize()
    #     self.assertDictEqual(result, {'age': [(1, None)], 'name': [(1, 'Kendall')]})

if __name__ == '__main__':
    unittest.main()
