class ModelOperation:
    dependencies = []
    actions = []
    initial = False
    
    def __init__(self, name, model):
        self.name = name
        self.model = model
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(<{self.name}>)"
    
    def __hash__(self) -> int:
        return hash(self.name)


class Operations(ModelOperation):
    """Operations allows to recreate a model sequence
    where the user would be able to recreate a
    data file from saved operations that was
    run from an initial scrapping"""
    model = None
    
    def __init__(self, name, model):
        super().__init__(name, model)
