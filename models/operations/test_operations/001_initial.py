from zineb.models import fields
from zineb.models.operations import actions
from zineb.models.operations.base import Operations


class Operation(Operations):
    model = 'test_model'
    # dependencies = [
    #     ('initial', '001_initial')
    # ]
    actions = [
        actions.AddValue('name', 'Kendall', fields.CharField(max_length=50, default='Kylie')),
        actions.AddValue('surname', 'Jenner', fields.CharField())
    ]
