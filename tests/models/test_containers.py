import unittest

from zineb.tests.models import items
from zineb.utils.containers import ModelSmartDict, SmartDict


class TestSmartDict(unittest.TestCase):
    def setUp(self):
        fields = ['name', 'age']
        container = SmartDict(*fields)
        container.model = items.BasicModel()
        self.container = container

    def test_can_update_field(self):
        # When there are many fields, like in the above, if we
        # update on column (ex. name), then age row should be None
        self.container.update('name', 'Kendall')
        self.assertDictEqual(self.container.as_values(), {'age': [None], 'name': ['Kendall']})

    def test_can_update_row(self):
        self.container.update('name', 'Kendall')
        self.container.update('age', 24)
        self.assertDictEqual(self.container.as_values(), {'age': [24], 'name': ['Kendall']})

    def test_final_container(self):
        result = self.container.as_values()
        self.assertIsInstance(result, dict)

    def test_can_add_multiple(self):
        self.container.update_multiple({'name': 'Kendall', 'age': 24})
        self.assertDictEqual(self.container.as_values(), {'age': [24], 'name': ['Kendall']})

        self.container.update_multiple({'name': 'Kylie', 'age': 22})
        self.assertDictEqual(self.container.as_values(), {'age': [24, 22], 'name': ['Kendall', 'Kylie']})

    def test_can_get_csv_type_values(self):
        self.container.update('name', 'Kendall')
        self.assertIsInstance(self.container.as_csv(), list)

        result = self.container.as_csv()
        # Expected [['name', 'age'], ['Kendall', 24]]
        self.assertEqual(result[1], ['Kendall', None])
        self.assertListEqual(result, [['name', 'age'], ['Kendall', None]])
        
    def test_elements_sorting(self):
        # True = Descending
        # False = Ascending
        fields = ['name', 'age']
        container = SmartDict(*fields, order_by=[['name', False]])
        
        data = [{'name': 'Kendall', 'age': 20}, {'name': 'Candice', 'age': 26}]
        
        result = container.apply_sort(data)
        self.assertListEqual(result, [{'name': 'Kendall', 'age': 20}, {'name': 'Candice', 'age': 26}])
        
        container.order_by = [['name', False], ['age', True]]
        result = container.apply_sort(data)
        self.assertListEqual(result, [{'name': 'Kendall', 'age': 20}, {'name': 'Candice', 'age': 26}])
        
        container.order_by = [['age', False]]
        result = container.apply_sort(data)
        self.assertListEqual(result, [{'name': 'Kendall', 'age': 20}, {'name': 'Candice', 'age': 26}])


class TestModelSmartDict(unittest.TestCase):
    def setUp(self):        
        self.container = ModelSmartDict(items.SimpleModel())
    
    def test_can_save_without_commit(self):
        self.container.update('name', 'Kendall')
        result = self.container.execute_save(commit=False)
        # NOTE: Technically we should receive a dict
        # but we're also using JSON dump, this returns
        # string
        self.assertIsInstance(result, str)
        
        
if __name__ == '__main__':
    unittest.main()
