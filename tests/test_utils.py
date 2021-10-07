import unittest
from utils.urls import reconstruct_url
import requests
from io import BytesIO
from zineb.utils.images import download_image
from zineb.utils.urls import replace_urls_suffix

# response = requests.get('https://www.hawtcelebs.com/wp-content/uploads/2021/01/kimberley-garner-in-a-colorful-bikini-at-a-beach-in-miami-01-07-2021-3.jpg')

# class TestDownloadImage(unittest.TestCase):
#     def test_down_resolution(self):
#         result = download_image(response)
#         self.assertIsInstance(result, tuple)

#         width, height, data = result
#         self.assertIsInstance(width, int)
#         self.assertIsInstance(height, int)
#         self.assertIsInstance(data, BytesIO)

#     def test_as_thumbnail(self):
#         result = download_image(response, as_thumbnail=True)


class TestProcessUrls(unittest.TestCase):
    def test_url_processor(self):
        urls = ['http://example.com/image_120.jpg']
        processed_urls = replace_urls_suffix(urls, '_120.jpg', '.jpg')
        self.assertListEqual(processed_urls, ['http://example.com/image.jpg'])


class TestReconstructUrl(unittest.TestCase):
    def test_url_reconstruction(self):
        url = 'https://example.com/image'
        result = reconstruct_url(url, pattern=r'(\/image$)')
        print(result)


if __name__ == "__main__":
    unittest.main()
