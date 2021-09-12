# a = {'a': [1, 2], 'b': 1}

# def test():
#     for key, values in a.items():
#         if isinstance(values, (list, tuple)):
#             for value in values:
#                 yield {key: value}
#         else:
#             yield {key: values}

# from collections.abc import Mapping, MutableMapping, KeysView
# from typing import OrderedDict


# import datetime

# import pytz
# from zineb.models.fields import AgeField, DateField

# t = pytz.timezone('America/Chicago')
# c = datetime.datetime.now().astimezone(t)
# d = datetime.datetime.strptime('2018-01-01', '%Y-%M-%d')
# c = d.astimezone(t)

# d = datetime.datetime.strptime('1-1-2017', '%d-%M-%Y')
# print(d.date())


from zineb.models.datastructure import Model
from zineb.models import fields
from zineb.models.expressions import When

class TestModel(Model):
    date = fields.IntegerField()

model = TestModel()
model.add_case(15, When('google__gt', 0))
print(model)
