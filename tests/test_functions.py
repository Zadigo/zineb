from zineb.models.datastructure import Model
from zineb.models import fields
from zineb.models.functions import ExtractMonth

class MyModel(Model):
    year = fields.DateField('%Y-%M-%d')

model = MyModel()
model.add_value('year', ExtractMonth('2021-1-1'))
print(model)
