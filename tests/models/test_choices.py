import unittest
from zineb.tests.models.items import ExampleChoices

class TestChoices(unittest.TestCase):
    def setUp(self):
        self.instance = ExampleChoices()
        
    def test_choice_in_choices(self):
        self.assertTrue('NAME' in self.instance)
        
    def test_can_convert_choice(self):
        self.assertEqual('Name', self.instance.convert('Name'))


if __name__ == '__main__':
    unittest.main()
