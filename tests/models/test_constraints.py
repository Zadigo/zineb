import unittest

from zineb.models.constraints import UniqueConstraint
from zineb.tests.models.items import BasicModel
from zineb.utils.containers import SmartDict


class TestConstraints(unittest.TestCase):
    def setUp(self):
        self.model = BasicModel()
        constraint = UniqueConstraint(['name'], 'unique_name')
        constraint.update_model_options(self.model)
        self.constraint = constraint

    def test_constraint_flags(self):
        self.assertIsNotNone(self.constraint.model)
        self.assertIsInstance(self.constraint._data_container, SmartDict)
        self.assertFalse(callable(self.constraint.condition))

    def test_check_constraint(self):
        self.constraint._data_container.update('name', 'Kendall')
        errors = self.constraint('Kendall')
        self.assertTrue(len(errors) == 1)
        self.assertIsInstance(errors[-0], tuple)


if __name__ == '__main__':
    unittest.main()
