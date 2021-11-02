import unittest

from zineb.html_parser.builders import BaseBuilder
from zineb.tests.html_parser import templates


class TestBuilder(unittest.TestCase):
    def setUp(self):
        builder = BaseBuilder()
        builder.start_iteration(templates.HTML1)
        builder.finalize()
        self.builder = builder

    def test_tree(self):
        self.assertGreater(self.builder.number_of_tags, 0)

    def test_tree_composition(self):
        self.assertIn('html', self.builder.html_tree)

        
if __name__ == '__main__':
    unittest.main()
