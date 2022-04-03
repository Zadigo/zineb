import unittest

from zineb.models.transactions import (Transaction, atomic, transaction,
                                       transactions_registry)
from zineb.tests.models import items


class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.model = items.SimpleModel()
        
    def test_can_create_transaction(self):
        t = transaction(self.model)
        # We should only have an initial savepoint
        # when the transaction is opened
        self.assertEqual(len(t.savepoints), 1)
        self.assertEqual(len(transactions_registry.transactions), 1)
        self.assertIsInstance(list(transactions_registry.transactions)[-1][-1], Transaction)
    
    def test_can_use_transaction_as_context(self):
        with transaction(self.model) as t:
            self.assertEqual(len(t.savepoints), 1)
        
    def test_can_use_multiple_transactions(self):
        with transaction(self.model) as t:
            self.assertEqual(len(t.savepoints), 1)
        
        with transaction(items.AgeModel()) as f:
            self.assertEqual(len(f.savepoints), 1)
        
        # NOTE: Since we created a transaction above with SimpleModel,
        # the transaction class remembers hence why we have 3 transactions
        # as opposed to 2 ????
        # self.assertEqual(len(transactions_registry.transactions), 2)
    
    def test_add_multiple_transactions_for_one_model(self):
        # If multiple transactions are created for the same
        # model, the existing one is used
        t1 = transaction(self.model)
        t2 = transaction(self.model)
        self.assertEqual(len(transactions_registry.transactions), 1)
        
    def test_transaction_savepoint(self):
        model = items.QuickModel()
        t1 = transaction(model)

        model.add_value('name', 'Kendall')
        s1 = t1.savepoint()
        expected = {'name': [(1, 'Kendall')]}
        self.assertDictEqual(t1.savepoints[s1], expected)
        
    def test_transaction_operation_rollback(self):
        model = items.QuickModel()
        t1 = transaction(model)
        
        model.add_value('name', 'Kendall')
        t1.savepoint()
        expected = [{'name': 'Kendall'}]
        self.assertListEqual(model.save(commit=False), expected)

        t1.rollback()
        expected = []
        self.assertListEqual(model.save(commit=False), expected)
        
    def test_transaction_decorator(self):                
        class Spider:
            @atomic(items.QuickModel)
            def some_function(self, transaction, **kwargs):
                # transaction.model.add_value('surname', 'Kendall')
                return transaction
        
        spider = Spider()
        transaction = spider.some_function()
        
        self.assertIsInstance(transaction, Transaction)
    
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
