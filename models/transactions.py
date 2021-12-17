from collections import defaultdict
from typing import Callable

from zineb.utils.characters import create_random_string
from zineb.utils.formatting import LazyFormat
from zineb.utils.iteration import keep_while


class TransactionsRegistry:
    transactions = set()
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.transactions})"
        
    def __iter__(self):
        return iter(self.transactions)
    
    def new(self, model, transaction_instance):
        self.transactions.add((model, transaction_instance))
        
transactions_registry = TransactionsRegistry()


class Transaction:
    """An interface for a model that can create specific
    states for a given model therefore allowing rollbacks
    either to a specific point or to the initial state
    """
    def __init__(self, model=None):
        self.savepoints = defaultdict(list)        
        self.model = model
        # Automatically create an initial
        # savepoint when the model is first
        # introduced to the interface
        self.savepoint()
        
    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model.__class__.__name__})"
    
    def __enter__(self, *args, **kwargs):
        if self.model is None:
            message = LazyFormat("{obj} should be an instance of Model. Got {obj_type}", obj=self.model, obj_type=type(self.model))
            raise TypeError(message)
        return self
    
    def __exit__(self, *args, **kwargs):
        return False
        
    @property
    def _initial_savepoint(self):
        keys = list(self.savepoints.keys())
        return keys[-0]
    
    @property
    def _last_savepoint(self):
        keys = list(self.savepoints.keys())
        return keys[-1]
    
    def savepoint(self):
        savepoint_name = create_random_string(lowercased=True)
        model_data = self.model._cached_result
        self.savepoints.update({savepoint_name: model_data.copy_values()})
        return savepoint_name
    
    def rollback(self, savepoint: str=None):
        if savepoint is None:
            self.model.values = self.savepoints[self._initial_savepoint]
        else:
            self.model.values = self.savepoints[savepoint]
    
    def rollback_on_error(self):
        """Rollback container on the first initial
        savepoint on a saving error"""
        return self.rollback(savepoint=self._initial_savepoint)
    
    def delete(self, savepoint: str):
        del self.savepoints[savepoint]


def transaction(model: Callable):
    existing_transaction = list(keep_while(lambda m: model in m, transactions_registry))
    if existing_transaction:
        _, instance = existing_transaction
    else:
        instance = Transaction(model=model)        
        transactions_registry.new(model, instance)
        
    return instance
