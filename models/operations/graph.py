from collections import defaultdict

from numpy import isin


class OperationsGraph:
    tree = defaultdict(set)
    
    def __init__(self, model=None):
        self.model = model
    
    def _add_root(self, name, klass):
        instance = klass(name=name, model=self.model)
        from zineb.models.operations.base import Operations
        if not isinstance(instance, Operations):
            raise ValueError('klass should be an instance of Operations')
        if 'initial' in name:
            operations = self.tree['test_model']
            operations.add((name, instance))
    
    def _add_child(self, name, klass, **kwargs):
        pass
    
    def create(self, name, klass, **kwargs):
        if 'initial' in name:
            self._add_root(name, klass)
            return True
        return self._add_child(name, klass)
        

# graph = OperationsGraph()
# class A:
#     def __init__(self, model):
#         pass
# graph.create('001_initial', A)
# print(graph.tree)
