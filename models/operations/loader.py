import os
from importlib import import_module

from numpy import number

from zineb.models.operations.graph import OperationsGraph


class OperationFilesLoader:
    """Loads all the operations files from a given 
    project, register them in the OperationsGraph 
    to be runned"""
    
    def __init__(self, model=None):
        self.graph = OperationsGraph(model=model)
        _, _, paths = next(os.walk('./models/operations/test_operations'))
        for path in paths:
            number, full_name, true_name = self._check_module_name(path)
            if number and true_name:
                module = import_module(f"models.operations.test_operations.{full_name}")
                # In each module we are looking for a 
                # subclass of Operations
                klass = getattr(module, 'Operations', None)
                if klass is None:
                    raise ValueError(f"{full_name} does not have any Operations subclass")
                self.graph.create(full_name, klass, number=number)
            
    @staticmethod
    def _check_module_name(name):
        if '__init__' in name:
            return False, False, False
        
        if not name.endswith('py'):
            raise ValueError('File is not a python module')
        
        full_name, ext = name.split('.')
        number, true_name = full_name.rsplit('_', maxsplit=1)
        
        if not number.isnumeric():
            raise ValueError(f"File does not follow valid naming convention. {number}")
        return number, full_name, true_name
            
            
            
from zineb.models.datastructure import Model
from zineb.models import fields
class A(Model):
    name = fields.CharField()

o = OperationFilesLoader(model=A)
print(o.graph.tree)
