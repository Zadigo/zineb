from zineb.models import fields
from zineb.models.operations import actions
from zineb.models.operations.base import Operations

class Operation(Operations):
    model = 'TestModel'
    actions = [
        fields.CharField(max_length=50)
    ]
