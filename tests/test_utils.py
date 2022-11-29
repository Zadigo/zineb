import unittest

from zineb.utils.formatting import (LazyFormat, remap_to_dict,
                                    reverse_remap_to_dict)
from zineb.utils.functionnal import LazyObject
from zineb.utils.iteration import (collect_files, drop_while, keep_while,
                                   regex_iterator, split_while)


class TestFormattingUtilities(unittest.TestCase):
    def test_lazy_format(self):
        text = LazyFormat('Kendall {name}', name='Jenner')
        self.assertEqual(str(text), 'Kendall Jenner')

    def test_remap_to_dict(self):
        data = remap_to_dict({'a': [1, 2]})
        self.assertListEqual(data, [{'a': 1}, {'a': 2}])

    def test_reverse_remap_to_dict(self):
        data = reverse_remap_to_dict([{'a': 1}, {'a': 2}])
        self.assertDictEqual(data, {'a': [1, 2]})


class TestIterationUtilities(unittest.TestCase):
    def test_keep_while(self):
        data = keep_while(lambda x: x == 1, [1, 2])
        self.assertListEqual(list(data), [1])

    def test_drop_while(self):
        data = drop_while(lambda x: x == 1, [1, 2])
        self.assertListEqual(list(data), [2])

    def test_split_while(self):
        data = split_while(lambda x: x == 1, [1, 2])
        self.assertListEqual(list(data), [[1], [2]])

    # def test_collect_files(self):
    #     from zineb.settings import settings
    #     settings(PROJECT_PATH=None)
    #     files = collect_files('test_htmls')
    #     self.assertTrue(len(files) > 0)


# from zineb.utils.characters import replace_escape_chars, strip_white_space, deep_clean
# from zineb.utils.images import download_image
# from zineb.utils.urls import replace_urls_suffix

# class TestReplaceEscapeCharacters(unittest.TestCase):
#     def test_replacement(self):
#         values = [
#             'Kendall Jenner',
#             '\n\n\n\n\nKendall Jenner',
#             '\n\n\t\n\nKendall Jenner',
#             '\n\r\r\n\nKendall Jenner\r\n',
#         ]
#         for value in values:
#             with self.subTest(value=value):
#                 self.assertEqual(replace_escape_chars(value), 'Kendall Jenner')


# class TestStripWhitespace(unittest.TestCase):
#     def test_replacement(self):
#         values = [
#             '\t\nKendall\rJenner',
#             '\x0c\x0c\tKendall\rJenner\r\n'
#         ]
#         for value in values:
#             with self.subTest(value=value):
#                 self.assertEqual(strip_white_space(value), 'Kendall\rJenner')


# class TestDeepCleaning(unittest.TestCase):
#     def test_replacement(self):
#         values = [
#             '\t\nKendall\rJenner',
#             '\x0c\x0c\tKendall\rJenner\r\n'
#         ]
#         for value in values:
#             with self.subTest(value=value):
#                 self.assertEqual(deep_clean(value), 'Kendall Jenner')


# class TestStripHtlmTags(unittest.TestCase):
#     pass

# class TestProcessUrls(unittest.TestCase):
#     def test_url_processor(self):
#         urls = ['http://example.com/image_120.jpg']
#         processed_urls = replace_urls_suffix(urls, '_120.jpg', '.jpg')
#         self.assertListEqual(processed_urls, ['http://example.com/image.jpg'])


# class TestReconstructUrl(unittest.TestCase):
#     def test_url_reconstruction(self):
#         url = 'https://example.com/image'
#         result = reconstruct_url(url, pattern=r'(\/image$)')
#         print(result)

if __name__ == '__main__':
    unittest.main()
