from typing import OrderedDict

# { 001_initial: [instance, { (002, instance), (003, instance) }] }

class MigrationStore:
    initial_root = None
    tree = dict()
    
    def add(self, name, instance, **kwargs):
        if 'initial' in name:
            self.add_root(name, instance)
        else:
            self.add_child(name, instance)
    
    def add_root(self, name, instance):
        if 'initial' not in self.tree:
            self.initial_root = name
            self.tree[self.initial_root] = [instance, set()]
            
    def add_child(self, name, instance):
        initial_root = self.tree[self.initial_root]
        initial_instance = initial_root[0]
        children = initial_root[-1]
        children.add((name, instance))
        self.tree[self.initial_root] = [initial_instance, children]
