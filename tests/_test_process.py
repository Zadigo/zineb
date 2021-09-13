# import datetime

# import pytz
# from zineb.models.fields import AgeField, DateField

# t = pytz.timezone('America/Chicago')
# c = datetime.datetime.now().astimezone(t)
# d = datetime.datetime.strptime('2018-01-01', '%Y-%M-%d')
# c = d.astimezone(t)

# d = datetime.datetime.strptime('1-1-2017', '%d-%M-%Y')
# print(d.date())


# from zineb.models.datastructure import Model
# from zineb.models import fields
# from zineb.models.expressions import When

# class TestModel(Model):
#     date = fields.IntegerField()

# model = TestModel()
# model.add_case(15, When('google__gt', 0))
# print(model)

from models.expressions import ExtractYear
from zineb.models.datastructure import Model
from zineb.models import fields
from zineb.models.expressions import Add

class TestModel(Model):
    dob = fields.RegexField(r'(\d+)', output_field=fields.CharField())

model = TestModel()
model.add_value('dob', Add('100€', 10))
print(model)
