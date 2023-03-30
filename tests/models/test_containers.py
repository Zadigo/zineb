import unittest

from zineb.tests.models import items
from zineb.utils.containers import (Column, Columns, ModelSmartDict, Row,
                                    SmartDict)


class TestSmartDict(unittest.TestCase):
    def setUp(self):
        fields = ['name', 'age']
        container = SmartDict(*fields)
        self.container = container

    def test_columns(self):
        instance = Columns(self.container)
        self.assertEqual(instance.__len__(), 2)
        self.assertIsInstance(instance.get_column('name'), Column)
        self.assertListEqual(instance.declared_fields, ['name', 'age'])
        self.assertFalse(instance.synchronizer.get_last_row)
        self.assertEqual(instance.first.index, 0)
        self.assertIsNotNone(instance.get_column_at_index(0))

    def test_column(self):
        columns = Columns(self.container)
        instance = Column(columns, 1, 'name')
        self.assertEqual(instance._column_name, 'Name')
        self.assertEqual(instance.__len__(), 0)

    def test_row(self):
        columns = Columns(self.container)
        instance = Column(columns, 1, 'name')
        # Test on new row
        instance.add_new_row('name', 'Kendall Jenner', id_value=1)

        # Test on Column
        self.assertListEqual(instance.colum_values, ['Kendall Jenner'])
        expected_list = [
            Row(1, 'name', 'Kendall Jenner', ['name', 'age'])
        ]
        self.assertListEqual(instance.column_rows, expected_list)
        self.assertListEqual(instance.get_column_values, ['Kendall Jenner'])
        self.assertDictEqual(
            instance.get_row_values,
            {'name': 'Kendall Jenner', 'age': None}
        )
        self.assertTrue(instance == 'name')
        self.assertEqual(instance.__len__(), 1)

        # Test on synchronizer
        synchronizer = instance._columns_instance.synchronizer
        self.assertSetEqual(synchronizer.current_updated_columns, {'name'})
        self.assertEqual(len(synchronizer.column_rows), 1)
        self.assertTrue(synchronizer.get_last_row['id'] == 1)

        # Test when updating the same column - Expected:
        # since we're updating the same column, then a
        # new row is created which makes that we should
        # still have name
        self.assertSetEqual(synchronizer.current_updated_columns, {'name'})
        # Which is different from this case where we are
        # updating the same row but a different column and
        # in this case we should be updating the last created
        # row as opposed to creating a new one
        instance.add_new_row('age', 24, id_value=2)
        self.assertSetEqual(
            synchronizer.current_updated_columns,
            {'name', 'age'}
        )
        self.assertEqual(len(synchronizer.column_rows), 1)

        synchronizer.reset()
        self.assertListEqual(synchronizer.column_rows, [])

    def test_row_class(self):
        row = Row(1, 'name', 'Kendall Jenner', ['name', 'age'])
        self.assertTrue(row.id == 1)
        self.assertTrue(row.name == 'Kendall Jenner')
        self.assertTrue(1 in row)
        self.assertFalse(row > 2)
        self.assertTrue(row >= 1)
        other_row = Row(2, 'name', 'Kylie Jenner', ['name', 'age'])
        self.assertTrue(row != other_row)

    def test_high_profile_load(self):
        instance = SmartDict.new_instance('name')

        celebrities = [
            'Kendall Jenner',
            'Kylie Jenner',
            'Anya Maya Taylor',
            'Maria Sharapova',
            'Greta Thunberg',
            'Victoria Azarenka',
            'Eugenie Bouchard',
            'Lucie Safarova',
            'Pia Mia',
            'Coy Leray',
            'Margot Robie'
        ]

        for i, celebrity in enumerate(celebrities):
            with self.subTest(celebrity=celebrity):
                instance.update('name', celebrity, id_value=i)
        rows = instance.columns.synchronizer.column_rows
        self.assertTrue(len(rows) == len(celebrities))
        self.assertTrue(instance.columns.first.first_row['id'] == 0)
        self.assertTrue(instance.columns.last.last_row['id'] == 10)

    def test_data_integrity(self):
        pass

    def test_can_update_field(self):
        # When there are many fields, like in the above, if we
        # update on column (ex. name), then age row should be None
        self.container.update('name', 'Kendall')
        self.container.update('age', 24)
        self.assertDictEqual(
            self.container.columns.as_values,
            {
                'name': ['Kendall'],
                'age': [24]
            }
        )

    def test_field_balancing(self):
        # Test that there is a balance EVEN
        # when unbalanced values are input
        self.container.update('name', 'Kendall Jenner')
        self.container.update('name', 'Kylie Jenner')
        self.container.update('age', 26)
        records = self.container.columns.as_values
        values_for_name = records['name']
        values_for_age = records['age']
        self.assertTrue(len(values_for_name) == len(values_for_age))

    def test_final_output_containers(self):
        self.container.update('name', 'Kendall Jenner')
        self.container.update('age', 25)

        result = self.container.columns.as_records
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertTrue('name' in result[0])
        self.assertTrue('age' in result[0])

        result = self.container.columns.as_values
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['name'], list)

        result = self.container.columns.as_csv
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], list)

    def test_add_multiple_method(self):
        self.container.update_multiple({'name': 'Kendall', 'age': 24})
        # FIXME: Seems like when using this function
        # multiple times, the output value with as_values
        # becomes a dict as opposed to a list
        self.assertListEqual(
            self.container.columns.as_values,
            [['name', 'age'], ['Kendall'], [24]]
        )

        self.container.update_multiple({'name': 'Kylie', 'age': 22})
        self.assertListEqual(
            self.container.columns.as_values,
            [['name', 'age'], ['Kendall', 24], ['Kylie', 22]]
        )

    def test_csv_output_values(self):
        self.container.update('name', 'Kendall')
        self.assertIsInstance(self.container.columns.as_csv, list)

        result = self.container.columns.as_csv
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
