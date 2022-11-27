import unittest
from zineb.tests.models.items import BasicModel
from zineb.models.constraints import CheckConstraint, UniqueConstraint
from zineb.utils.containers import SmartDict


class TestConstraints(unittest.TestCase):
    def setUp(self):
        model = BasicModel()
        constraint = UniqueConstraint(['name', 'surname'], 'unique_name')
        constraint.values = {'name': ['Kendall'], 'surname': ['Jenner']}
        constraint.prepare(model)
        self.constraint = constraint

    def test_constraint_flags(self):
        self.assertIsNotNone(self.constraint.model)
        self.assertIsInstance(self.constraint._data_container, SmartDict)
        self.assertFalse(callable(self.constraint.condition))

    def test_check_constraint(self):
        result = self.constraint.check_constraint('Kendall')
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
