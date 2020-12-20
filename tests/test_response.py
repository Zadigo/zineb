import unittest
from zineb.http.responses import HTMLResponse
from zineb.http.request import HTTPRequest

request = HTTPRequest('http://example.com')
request._send()

class TestHTMLResponse(unittest.TestCase):
    def setUp(self):
        self.html_response = HTMLResponse(request.html_response)

    def test_page_title(self):
        self.assertEqual(self.html_response.page_title, 'Example Domain')


if __name__ == "__main__":
    unittest.main()
