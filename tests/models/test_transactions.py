import unittest

from zineb.models.transactions import transaction, transactions_registry
from zineb.tests.models import items


class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.model = items.SimpleModel()
        
    def test_can_create_transaction(self):
        t = transaction(self.model)
        # We should only have an initial savepoint
        # when the transaction is opened
        self.assertEqual(len(t.savepoints), 1)
    
    def test_can_use_transaction_as_context(self):
        with transaction(self.model) as t:
            self.assertEqual(len(t.savepoints), 1)
        
    def test_can_use_multiple_transactions(self):
        with transaction(self.model) as t:
            self.assertEqual(len(t.savepoints), 1)
        
        with transaction(items.AgeModel()) as f:
            pass
        
        # NOTE: Since we created a transaction above with SimpleModel,
        # the transaction class remembers hence why we have 3 transactions
        # as opposed to 2
        self.assertEqual(len(transactions_registry.transactions), 3)
    
    def test_cannot_add_multiple_transactions_for_one_model(self):
        pass
        
    
class TestInlineTransaction(unittest.TestCase):
    def test_can_do_inline_transaction(self):
        model = items.SimpleModel()
        # 1. Open a transaction
        t = transaction(model)
        # 2. Save an item to the model
        t.model.add_value('name', 'Kendall')
        # 3. Save the model's data current
        # state
        s1 = t.savepoint()
        # 4. Add another value to the model. Since savepoint
        # has not be called a second time, we should only
        # have the previous state e.g. name with Kendall
        t.model.add_value('name', 'Kylie')

        expected = {'age': [(1, None)], 'name': [(1, 'Kendall')], 'date_of_birth': [(1, None)]}
        self.assertDictEqual(dict(t.savepoints[s1]), expected)
        expected = {'age': [(1, None), (2, None)], 'name': [(1, 'Kendall'), (2, 'Kylie')], 'date_of_birth': [(1, None), (2, None)]}
        self.assertDictEqual(t.model._cached_result.values, expected)


class TestTransactionOperations(unittest.TestCase):
    # This class was created apart in order to test
    # operations for transactions and also to make sure
    # that we are dealing with a single model
    
    def setUp(self):
        self.model = items.SimpleModel()
        
    def test_can_create_savepoint(self):
        with transaction(self.model) as t:
            t.model.add_value('name', 'Julie')
            s1 = t.savepoint()
            self.assertEqual(len(t.savepoints), 2)

    def test_can_rollback_savepoint(self):
        with transaction(self.model) as t:
            t.model.add_value('name', 'Julie')
            s1 = t.savepoint()
            t.rollback(s1)
            self.assertEqual(t.model._cached_result.as_list(), [])


if __name__ == '__main__':
    unittest.main()
