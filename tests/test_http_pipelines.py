from zineb.http.pipelines import Pipeline
import unittest

def do_something_here(response):
    print(response)

pipeline = Pipeline(['http://example.com', 'http://example.com'], [do_something_here])


class TestPipeline(unittest.TestCase):
    def test_resolution(self):
        self.assertIsInstance(pipeline.responses, list)

if __name__ == "__main__":
    unittest.main()
