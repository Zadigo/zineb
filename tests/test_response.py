from http.request import JsonRequest
import unittest
from zineb.http.responses import HTMLResponse, ImageResponse
from zineb.http.request import HTTPRequest

request = HTTPRequest('http://example.com')
request._send()

image_request = HTTPRequest('https://www.hawtcelebs.com/wp-content/uploads/2021/01/kimberley-garner-in-a-colorful-bikini-at-a-beach-in-miami-01-07-2021-8.jpg')
image_request._send()

class TestHTMLResponse(unittest.TestCase):
    def setUp(self):
        self.html_response = HTMLResponse(request.html_response)

    def test_page_title(self):
        self.assertEqual(self.html_response.page_title, 'Example Domain')


class TestImageResponse(unittest.TestCase):
    def setUp(self):
        self.image_response = ImageResponse(image_request._http_response)

    def test_result(self):
        self.image_response.save()


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(TestImageResponse('test_result'))
    runner.run(suite)
