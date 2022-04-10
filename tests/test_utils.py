import unittest

from zineb.utils.functionnal import LazyObject

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


if __name__ == "__main__":
    unittest.main()
