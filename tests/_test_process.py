# import datetime

# import pytz
# from zineb.models.fields import AgeField, DateField

# t = pytz.timezone('America/Chicago')
# c = datetime.datetime.now().astimezone(t)
# d = datetime.datetime.strptime('2018-01-01', '%Y-%M-%d')
# c = d.astimezone(t)

# d = datetime.datetime.strptime('1-1-2017', '%d-%M-%Y')
# print(d.date())


from zineb.models.expressions import ExtractYear
from zineb.models.datastructure import Model
from zineb.models import fields
from zineb.models.expressions import Add

class TestModel(Model):
    year = fields.DateField(default='*')

model = TestModel()
model.add_value('year', ExtractYear('11-1-2021', output_field=fields.ListField()))
print(model)
