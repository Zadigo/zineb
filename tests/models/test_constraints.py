import unittest

from zineb.models.constraints import CheckConstraint, UniqueConstraint


class TestConstraints(unittest.TestCase):
    def setUp(self):
        constraint = UniqueConstraint(['name', 'surname'], 'unique_name')
        constraint.values = {
            'name': ['Kendall'],
            'surname': ['Jenner']
        }
        constraint.prepare()
        self.constraint = constraint
        
    def test_check_constraint(self):
        result = self.constraint.check_constraint('Kendall')
        self.assertIsNone(result)
        
        
if __name__ == '__main__':
    unittest.main()
