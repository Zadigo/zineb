# import unittest
# from zineb.extractors.base import TableExtractor, MultiTablesExtractor
# from zineb.tests import file_opener

# class TestRowsExtractor(unittest.TestCase):
#     def setUp(self):
#         self.extractor = TableExtractor()
#         self.soup = file_opener('tests/html/tables3.html')

#     def test_resolution(self):
#         result = self.extractor.resolve(self.soup)
#         self.assertIsInstance(result, list)
#         self.assertListEqual(self.extractor.values, [['1', '2']])

#     def test_resolution_of_table_with_class(self):
#         instance = self.extractor(class_name='second-table')
#         instance.resolve(self.soup)
#         self.assertEqual(instance.values, [['3', '4']])

#     def test_resolution_with_headers(self):
#         pass

#     def test_no_empty_rows(self):
#         instance = self.extractor(class_name='fourth-table', filter_empty_rows=True)
#         instance.resolve(self.soup)
#         self.assertListEqual(instance.values, [['7']])

#     # def test_using_specific_table(self):
#     #     rows = self.extractor.resolve(tables[10])
#     #     self.assertIsInstance(rows, list)
#     #     self.assertIsInstance(rows[-1], list)
#     #     self.assertIn('Erika', rows[2])

#     # def test_processors(self):
#     #     def replace_empty_values(value, row=None):
#     #         if value is None or value == '':
#     #             return None
#     #         else:
#     #             return value

#     #     extractor = TableExtractor(has_headers=True, processors=[
#     #                                replace_empty_values])
#     #     rows = extractor.resolve(player_table)
#     #     self.assertNotIn('', rows[2])

#     # def test_pandas_resolution(self):
#     #     extractor = TableExtractor()
#     #     df = extractor.resolve_to_dataframe(soup2)
#     #     self.assertIsInstance(df, pandas.DataFrame)

# if __name__ == '__main__':
#     unittest.main()
