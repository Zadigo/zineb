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

from zineb.models import fields
from zineb.models.constraints import CheckConstraint, UniqueConstraint
from zineb.models.datastructure import Model
import pickle

class Tournament(Model):
    location = fields.CharField()


class Player(Model):
    full_name = fields.CharField()
    tournaments = fields.RelatedModel(Tournament, relation_name='some_relation')
    
model = Player()
# print(model._meta.include_id_field)
# model.add_value('full_name', 'Kendall Jenner')
# model.add_value('full_name', 'Hailey Baldwin')
# model.tournament.add_value('location', 'Paris')
# print(model)
# model.tournaments.add_value('location', 'Paris')
# model = Tournament()
# print(model.tournament_set)
# print(model)
# print(pickle.dumps(model))
# print(model == model2)
print(model.id)
