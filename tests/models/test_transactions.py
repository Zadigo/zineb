import unittest

from zineb.models.transactions import transaction, transactions_registry
from zineb.tests.models import items


class TestTransaction(unittest.TestCase):
    def test_can_create_transaction(self):
        t = transaction(items.SimpleModel())
    
    def test_can_use_transaction_as_context(self):
        with transaction(items.SimpleModel()) as t:
            pass
        
    def test_can_use_multiple_transactions(self):
        with transaction(items.SimpleModel()) as t:
            pass
        
        with transaction(items.AgeModel()) as f:
            pass
        print(transactions_registry)
        self.assertEqual(len(transactions_registry.transactions), 2)
    
    def test_cannot_add_multiple_transactions_for_one_model(self):
        pass

if __name__ == '__main__':
    unittest.main()
    
    
# model = items.SimpleModel()
# with transaction(model) as t:
#     t.model.add_value('name', 'Kendall')
#     s1 = t.savepoint()
    
#     t.model.add_value('name', 'Kylie')
#     s2 = t.savepoint()
    
# print(t.model)


# model = items.SimpleModel()
# t = transaction(model)
# t.model.add_value('name', 'Kendall')
# s1 = t.savepoint()
# t.model.add_value('name', 'Kylie')
# # t.rollback(s1)
# s2 = t.savepoint()
# print(t.savepoints)
