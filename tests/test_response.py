import unittest

import pandas
from zineb.http.responses import HTMLResponse, ImageResponse, JsonResponse
from zineb.tests import create_test_request
from bs4.element import Tag

from tests import create_test_image_request, create_test_json_request

_request = create_test_request()

class TestHTMLResponse(unittest.TestCase):
    def setUp(self):
        self.html_response = HTMLResponse(_request.html_response)

    def test_page_title(self):
        self.assertEqual(self.html_response.page_title, 'Example Domain')

    def test_number_of_links(self):
        self.assertEqual(len(self.html_response.links), 1)

    def test_can_call_beautifulsoup_attributes_directly(self):
        tag = self.html_response.find('a')
        self.assertIsNotNone(tag)
        self.assertIsInstance(tag, Tag)


# _image_request = create_test_image_request()

# class TestImageResponse(unittest.TestCase):
#     def setUp(self):
#         self.image_response = ImageResponse(_image_request._http_response)

#     def test_saving_to_media_folder(self):
#         self.image_response.save(path='tests/media')


# _json_response = create_test_json_request()

# class TestJsonResponse(unittest.TestCase):
#     def setUp(self):
#         self.json_response = JsonResponse(_json_response._http_response)

#     def test_raw_data_first_value(self):
#         self.assertIsInstance(self.json_response.raw_data[0], dict)

#     def test_response_data(self):
#         self.assertIsInstance(self.json_response.response_data, pandas.DataFrame)


if __name__ == "__main__":
    # runner = unittest.TextTestRunner()
    # suite = unittest.TestSuite()
    # suite.addTest(TestImageResponse('test_result'))
    # runner.run(suite)
    unittest.main()
