from collections import defaultdict
from typing import Callable

from zineb.utils.characters import create_random_string
from zineb.utils.formatting import LazyFormat
from zineb.utils.iteration import keep_while


class TransactionsRegistry:
    """Keeps track of all opened transactions"""
    
    transactions = set()
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.transactions})"
        
    def __iter__(self):
        return iter(self.transactions)
    
    def new(self, model, transaction_instance):
        self.transactions.add((model, transaction_instance))
        
    def close(self, model):
        del self.transactions[model]
        
transactions_registry = TransactionsRegistry()


class Transaction:
    """An interface which creates specific states of a model's
    data therefore allowing rollbacks either to a specific point 
    or to a initial one
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
        try:
            model_data = self.model._cached_result
        except:
            # If the element does not have a _cached_result,
            # then it's not a model instance
            raise TypeError(LazyFormat("'{obj}' is not an instance of Model", obj=self.model))
        self.savepoints.update({savepoint_name: model_data.copy_values()})
        return savepoint_name
    
    def rollback(self, savepoint: str=None):
        if savepoint is None:
            data_to_use = self.savepoints[self._initial_savepoint]
        else:
            data_to_use = self.savepoints[savepoint]
        self.model._cached_result._rollback_data_to(data_to_use)
    
    def rollback_on_error(self):
        """Rollback container on the first initial
        savepoint on a saving error"""
        return self.rollback(savepoint=self._initial_savepoint)
    
    def delete(self, savepoint: str):
        del self.savepoints[savepoint]


def transaction(model: Callable):
    """Opens a new transaction by binding a model
    to a Transaction class"""
    existing_transaction = list(keep_while(lambda m: model in m, transactions_registry))
    if existing_transaction:
        _, instance = existing_transaction
    else:
        instance = Transaction(model=model)        
        transactions_registry.new(model, instance)
        
    return instance


def atomic(model):
    """A decorator that allows you to wrap a definition
    as being part of a transaction
    
    Example
    -------
    
        class TestSpider(Model):
            @atomic(SimpleModel)
            def start(self, response, request, transaction, **kwargs):
                transaction.model.add_value('name', 'Kendall')
                transaction.savepoint()
    """
    def wrapper(func):        
        def start(self, response=None, request=None, transaction=None, **kwargs):
            transaction = Transaction(model=model())
            return func(self, response=response, request=request, transaction=transaction, **kwargs)
        return start
    return wrapper
