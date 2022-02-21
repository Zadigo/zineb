from zineb.db.migrations.base import Migrations
from zineb.db.migrations.operations import CreateModel
from zineb.models import fields


class Migration(Migrations):
    initial = True
    actions = [
        CreateModel(
            name='TestModel',
            fields=[
                ('name', fields.CharField(max_length=100, default='Kendall'))
            ]
        )
    ]
