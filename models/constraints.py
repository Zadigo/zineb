from typing import Any

from zineb.exceptions import ModelConstraintError


class UniqueConstraint:
    def __init__(self, name: str, *fields):
        self.fields = list(fields)
        self.name = name
        self.model = None
        
    def check_constraint(self, value: Any):
        from zineb.models.datastructure import Model
        
        if self.model is None:
            raise ValueError('A model should be provided')
        
        if not isinstance(self.model, Model):
            raise ValueError('Model should be an instance of Model')
        
        for field in self.fields:
            container = self.model._cached_result.get_container(field)
            if value in container:
                raise ModelConstraintError(field, value)
