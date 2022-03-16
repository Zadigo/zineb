# from zineb.management import execute_command_inline
# import sys
# import os
# os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'tests.testproject.settings')
# execute_command_inline([os.path.abspath(__file__), 'createspider', 'Temptation'])
# execute_command_inline(sys.argv)

# from argparse import ArgumentParser
# parser = ArgumentParser()
# parser.add_argument('command')
# parser.add_argument('project')
# parser.add_argument('--settings')
# namespace = parser.parse_args()
# print(namespace)



# from models.functions import Add, ExtractDay, ExtractYear, Substract
# from zineb.models import fields
# from zineb.models.datastructure import Model
# from zineb.models.functions import When

# class TestModel(Model):
#     age = fields.CharField()

# model = TestModel()

# print(model)

# from zineb.utils._datastructures import SmartDict


# s = SmartDict('name', 'surname')
# s.update('name', 'Kendall')
# s.update('surname', 'Jenner')
# s.update('name', 'Kylie')
# print(s.save(extension='csv'))

from zineb.models import fields
from zineb.models.datastructure import Model
from zineb.models.functions import Add, Substract, Multiply, Divide


class MyModel(Model):
    name = fields.CharField()
    age = fields.IntegerField()
    other = fields.ListField()
            

m = MyModel()
# m.add_value('name', ExtractDay('25-1-2021'))
# m.add_value('name', 'Kendall   <a>Jenner</a>')
# m.add_case('Kendal', When('name__eq=Kendal', 'Kendall'))
# m.add_value('name', '   Kendall    Jenner')
m.add_calculated_value('age', 15, Add(1), Add(1))
print(m)
