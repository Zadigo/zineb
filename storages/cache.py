from collections import OrderedDict

class StorageCache:
    memory = OrderedDict()

    def has_file(self, name):
        return self.memory.get(name)

    def get_files(self):
        return self.memory.values()

    def get(self, name):
        return self.memory.get(name)

    def update(self, name, obj):
        self.memory[name] = obj
        return self.memory
