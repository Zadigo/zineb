import unittest
from zineb.html_parser.tags import BaseTag, Tag

class TestTag(unittest.TestCase):
    def setUp(self):
        self.tag = Tag('html', {})

    def test_category(self):
        self.assertEqual(self.tag.category, 'tag')
        self.assertFalse(self.tag.is_closing_tag)


if __name__ == '__main__':
    unittest.main()
