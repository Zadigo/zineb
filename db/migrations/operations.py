class ModelOperations:
    def __init__(self, name):
        self.name = name


class CreateModel(ModelOperations):
    def __init__(self, name, fields):
        self.fields = fields
        super().__init__(name)
        