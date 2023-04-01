import unittest

from tests.models import items
from zineb.models.constraints import UniqueConstraint
from zineb.utils.containers import SmartDict


class TestConstraints(unittest.TestCase):
    def setUp(self):
        self.model = items.BasicModel()
        constraint = UniqueConstraint(['name'], 'unique_name')
        constraint.update_model_options(self.model)
        self.constraint = constraint

    def test_constraint_flags(self):
        self.assertIsNotNone(self.constraint.model)
        self.assertIsInstance(self.constraint._data_container, SmartDict)
        self.assertFalse(callable(self.constraint.condition))

    def test_fail_constraint(self):
        # Update the model using the proxy _data_container
        self.constraint._data_container.update('name', 'Kendall')
        self.constraint._data_container.update('name', 'Kendall')
        errors = self.constraint('Kendall')
        self.assertTrue(len(errors) == 1)
        self.assertIsInstance(errors[-0], tuple)

    def test_constraint_method(self):
        def some_condition(value):
            pass

        model = items.BasicModel()
        constraint = UniqueConstraint(
            ['name', 'age'],
            'one_age_per_name',
            some_condition
        )
        constraint.update_model_options(model)
        constraint._data_container.update('name', 'Kendall')
        errors = constraint('Kendall')

if __name__ == '__main__':
    unittest.main()
