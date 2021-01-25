import unittest
import requests
from io import BytesIO
from zineb.utils.general import download_image

response = requests.get('https://www.hawtcelebs.com/wp-content/uploads/2021/01/kimberley-garner-in-a-colorful-bikini-at-a-beach-in-miami-01-07-2021-3.jpg')

class TestDownloadImage(unittest.TestCase):
    def test_down_resolution(self):
        result = download_image(response)
        self.assertIsInstance(result, tuple)

        width, height, data = result
        self.assertIsInstance(width, int)
        self.assertIsInstance(height, int)
        self.assertIsInstance(data, BytesIO)

    def test_as_thumbnail(self):
        result = download_image(response, as_thumbnail=True)

if __name__ == "__main__":
    unittest.main()
