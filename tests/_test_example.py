from zineb.models.datastructure import Model
from zineb.models import fields

def name_validator(value):
    if value == 'Kendall Jenner':
        return 'Kylie'
    return value

class TestModel(Model):
    name = fields.CharField(null=False)

model = TestModel()
model.add_using_expression('name', 'a')
df = model.save(commit=False)
print(df)
