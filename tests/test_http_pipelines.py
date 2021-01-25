import unittest

from bs4 import BeautifulSoup
from zineb.http.pipelines import Pipeline

with open('tests/html/hawtcelebs.html') as f:
    soup = BeautifulSoup(f, 'html.parser')
    images = soup.find_all('img', attrs={'class': 'attachment-thumbnail'})
    srcs = []
    for image in images:
        if image.has_attr('src'):
            srcs.append(image.attrs.get('src'))

def do_something_here(response):
    return response

# pipeline = Pipeline(['http://example.com', 'http://example.com'], [do_something_here])
pipeline2 = Pipeline(srcs[:2], [do_something_here])


class TestPipeline(unittest.TestCase):
    def test_resolution(self):
        self.assertIsInstance(pipeline.responses, list)

    def test_resolution_two(self):
        self.assertIsInstance(pipeline2.responses, list)

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(TestPipeline('test_resolution_two'))
    runner.run(suite)
