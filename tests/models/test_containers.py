import unittest

from zineb.tests.models import items
from zineb.utils.containers import ModelSmartDict, SmartDict


class TestSmartDict(unittest.TestCase):
    def setUp(self):
        fields = ['name', 'age']
        container = SmartDict(*fields)
        self.container = container

    def test_can_update_field(self):
        # When there are many fields, like in the above, if we
        # update on column (ex. name), then age row should be None
        self.container.update('name', 'Kendall')
        self.container.update('age', 24)
        self.assertDictEqual(
            self.container.as_values(),
            {
                'age': [24],
                'name': ['Kendall']
            }
        )

    def test_field_balancing(self):
        # Test that there is a balance EVEN
        # when unbalanced values are input
        self.container.update('name', 'Kendall Jenner')
        self.container.update('name', 'Kylie Jenner')
        self.container.update('age', 26)
        values_for_name = self.container.get_container('name')
        values_for_age = self.container.get_container('age')
        self.assertTrue(len(values_for_name) == len(values_for_age))

    def test_final_output_containers(self):
        self.container.update('name', 'Kendall Jenner')
        self.container.update('age', 25)

        result = self.container.as_values()
        self.assertIsInstance(result, dict)
        self.assertTrue('name' in result)
        self.assertTrue('age' in result)

        result = self.container.as_list()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)

        result = self.container.as_csv()
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], list)

    def test_add_multiple_method(self):
        self.container.update_multiple({'name': 'Kendall', 'age': 24})
        self.assertDictEqual(
            self.container.as_values(),
            {
                'age': [24],
                'name': ['Kendall']
            }
        )

        self.container.update_multiple({'name': 'Kylie', 'age': 22})
        self.assertDictEqual(
            self.container.as_values(),
            {
                'age': [24, 22],
                'name': ['Kendall', 'Kylie']
            }
        )

    def test_csv_output_values(self):
        self.container.update('name', 'Kendall')
        self.assertIsInstance(self.container.as_csv(), list)

        result = self.container.as_csv()
        # If we only add one field e.g. name, then the
        # other field e.g. age should be None. Hence
        # the expected [['name', 'age'], ['Kendall', 24]]
        self.assertEqual(result[1], ['Kendall', None])
        self.assertListEqual(result, [['name', 'age'], ['Kendall', None]])

    # def test_can_add_smart_two_dicts(self):
    #     dict1 = SmartDict.new_instance('name', 'surname')
    #     dict2 = SmartDict.new_instance('name')
    #     new_dict = dict1 + dict2
    #     print(new_dict)

    def test_sorting_algorithm(self):
        # True = Descending
        # False = Ascending
        fields = ['name', 'age']
        container = SmartDict(*fields, order_by=[['name', False]])

        data = [
            {'name': 'Kendall', 'age': 20}, 
            {'name': 'Candice', 'age': 26}
        ]

        result = container.apply_sort(data)
        self.assertListEqual(
            result, 
            [
                {'name': 'Kendall', 'age': 20}, 
                {'name': 'Candice', 'age': 26}
            ]
        )

        container.order_by = [['name', False], ['age', True]]
        result = container.apply_sort(data)
        self.assertListEqual(
            result, 
            [
                {'name': 'Kendall', 'age': 20}, 
                {'name': 'Candice', 'age': 26}
            ]
        )

        container.order_by = [['age', False]]
        result = container.apply_sort(data)
        self.assertListEqual(
            result, 
            [
                {'name': 'Kendall', 'age': 20}, 
                {'name': 'Candice', 'age': 26}
            ]
        )


class TestModelSmartDict(unittest.TestCase):
    def setUp(self):
        self.container = ModelSmartDict(items.ConstrainedModel())

    def test_constraints(self):
        self.container.update_multiple({
            'name': 'Kendall',
            'surname': 'Jenner'
        })
        container = self.container.get_container('surname')
        self.container.run_constraints(container)


if __name__ == '__main__':
    unittest.main()
