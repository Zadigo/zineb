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
from zineb.models import fields
from zineb.models.datastructure import Model
# from zineb.models.functions import When

# class TestModel(Model):
#     age = fields.CharField()

# model = TestModel()
# model.add_value('age', 14)
# print(vars(model))

# print(model)

# from zineb.utils._datastructures import SmartDict


# s = SmartDict('name', 'surname')
# s.update('name', 'Kendall')
# s.update('surname', 'Jenner')
# s.update('name', 'Kylie')
# print(s.save(extension='csv'))

# from zineb.models.datastructure import Model
# from zineb.models.fields import DateField, IntegerField, AgeField, CharField, Value
# from zineb.models.functions import ExtractMonth, Substract, When


# class TestModel(Model):
#     age = CharField()
    
# m = TestModel()
# # m.add_calculated_value('age', 15, Substract(3))
# # m.add_case(15, When('age__gt=10', 15, 10))
# # m.add_value('age', 15)
# # m.add_value('age', Value('Kendall Jenner'))
# # m.update_model('age__gt=15')
# m.query(age__contains=14, name__contains='Kendall')
# print(m)

# from zineb.models.datastructure import Model
# from zineb.models import fields


# class MyModel(Model):
#     name = fields.CharField(max_length=-1, null=1)
#     pk = fields.IntegerField()
#     surname__ = fields.CharField()
#     created_on = fields.DateField(date_format=True)
    
# model = MyModel()

# print(model.checks())


# from zineb.utils.iteration import RequestQueue


# q = RequestQueue('http://example.com', 'https://jsonplaceholder.typicode.com/todos',
#                  'https://jsonplaceholder.typicode.com/posts', 'https://data.opendatasoft.com/api/records/1.0/search/?dataset=fr-esr-principaux-etablissements-enseignement-superieur%40mesr&q=&facet=type_d_etablissement&facet=siren', 'https://data.opendatasoft.com/api/records/1.0/search/?dataset=reseau-hta%40enedis&q=')
# q.prepare(type('Spider', (), {'meta': type('SpiderOptions', (), {'domains': []})}))
# print(q._iter())

# a = [{'name': 'Pauline'}, {'name': 'Kendall'}, {'name': 'Aurélie'}]
# print(sorted(a, key=lambda x: x['name']))

# from collections import namedtuple
# from zineb.management.commands.startproject import Command


# c = Command()
# namespace = namedtuple('namespace', ['project'])
# w = namespace('tests/creation')
# c.execute(w)
