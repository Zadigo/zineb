import sqlite3
from functools import cached_property

from zineb.db.schema import Schema


class SQliteBackend(Schema):
    def __init__(self, name):
        connection = sqlite3.connect(name)
        super().__init__(connection)


b = SQliteBackend('test.sqlite')

from zineb.models.datastructure import Model
from zineb.models import fields

class TestModel(Model):
    name = fields.CharField(default='Kendall')
    date_of_birth = fields.DateField()
    age = fields.IntegerField()
    
model = TestModel()

s = b.create_table_from_model(model)

# b.execute('SELECT name FROM table1', ('name', 'table2'))
