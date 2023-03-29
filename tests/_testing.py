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

# @total_ordering
# class V:
#     def __init__(self, value):
#         self.value = value

#     def __repr__(self):
#         return f'{self.__class__.__name__}([{self.value}])'

#     def __eq__(self, obj):
#         return obj == self.value

#     def __gt__(self, obj):
#         obj = self.convert_to_string(obj)
#         return len(self.value) > obj

#     def __contains__(self, obj):
#         obj = self.convert_to_string(obj)
#         return self.value in obj

#     def convert_to_string(self, value):
#         if isinstance(value, (int, float)):
#             return str(value)
#         return value

# class BaseConditions:
#     pass


# from zineb.models.datastructure import Model
# from zineb.models import fields
# class TestModel(Model):
#     name = fields.CharField()
#     surname = fields.NameField()

# model = TestModel()
# model.add_value('name', 'Kendall')
# model.add_value('name', 'Kendall')
# constraint = UniqueConstraint(['name', 'surname'], 'unique_name_and_surname')
# constraint.model = model
# constraint.prepare()
# print(constraint())


# from zineb.models.datastructure import Model
# from zineb.models import fields
# from zineb.models.constraints import UniqueConstraint
# from zineb.models.functions import ExtractYear
# from zineb.models.fields import Value


# class MyModel(Model):
#     name = fields.NameField()
#     surname = fields.NameField()

#     class Meta:
#         ordering = ['name']


# model = MyModel()
# # model.add_value('name', 'Kendall  ')
# model.add_value('name', 'Kylie')
# model.add_value('surname', 'Jenner')
# model.add_value('name', 'Kendall')
# model.add_value('surname', 'Jenner')
# print(model.surname)

# constraint = CheckConstraint(['name', 'surname'], 'unique_name', condition=lambda x: x == 15)
# constraint = UniqueConstraint(['name', 'surname'], 'unique_name', condition=lambda x: x == 15)
# constraint.values = {'name': ['Kendall'], 'surname': ['Jenner']}
# constraint.prepare(m)
# # print(constraint.check_constraint('Kendall'))
# print(constraint)

# from zineb.utils.containers import SmartDict
# from zineb.models import fields
# from zineb.models.datastructure import Model


# class Location(Model):
#     name = fields.CharField()


# class Celebrity(Model):
#     fullname = fields.CharField()
#     location = fields.RelatedModel(Location)


# model = Celebrity()

# model.add_value('fullname', 'Kendall Jenner')
# model.location.add_value('name', 'Paris')
# print(model.save(commit=False))


# from zineb.models.datastructure import Model
# from zineb.models import fields
# from zineb.models.relationships import OneToOneRelationship


# class Location(Model):
#     name = fields.CharField()


# class Height(Model):
#     value = fields.IntegerField()


# class Celebrity(Model):
#     fullname = fields.CharField()
#     # Resolve the fact that attributes point
#     # to the wrong things
#     location = fields.RelatedModel(Location)
#     height = fields.RelatedModel(Height)


# model1 = Location()
# model2 = Celebrity()

# FIXME: Why does the first addition to the related model
# is successful while there is no related value ?
# Expected: Should not be able to add any value in the
# in the model if there is no corresponding value in
# the related model
# model2.add_value('fullname', 'Kendall Jenner')
# model2.location.add_value('name', 'USA')
# model2.height.add_value('value', 174)
# model2.add_value('fullname', 'Kylie Jenner')
# model2.height.add_value('value', 156)
# print(model2)

# FIXME: There's an unbalance between two different
# related models when the values are added as below.
# "location" has 2 values while "height" has only one.
# Solution 1: Either we have an orchestrator that can
# see both models who know nothing about one another
# ensure that when one field is added in one, the other
# gets the same field
# Solution 2: Either we leave the unbalance and when the
# would want to to resolve the fields, raise
# a ForeignKey error
# model2.height.add_value('value', 156)
# model2.location.add_value('name', 'FRA')
# model2.location.add_value('name', 'ITA')
# print(model2.location)

# model2.add_value('fullname', 'Kendall Jenner')
# model2.location.add_value('name', 'FRA')
# model2.height.add_value('value', 180)
# model2.add_value('fullname', 'Kylie Jenner')
# FIXME: In this configuration, we only get one item
# in the column height, the one from above. This one
# does not get saved in the model
# Expected: We should be creating a new row
# not updating the last one
# BUG: SmartDict.update both the self._last_created_row
# is True and the name is not in self._current_updated_field and
# since there is a last_created_row, the logic
# moves to updating the last created row
# model2.height.add_value('value', 150)
# print(model2.height)

# r = OneToOneRelationship()
# r.update_relationship_options(model2)
# print(r.resolve_relationships())

# TODO: Check is there are checks for when an item that is not
# a model is passed in the RelatedModel field


# TEST for datastructures

from zineb.utils.containers import Column, Columns
from zineb.utils.containers import SmartDict, Column, Columns, Row

db = SmartDict('name', 'age', 'country')
# db2 = SmartDict('name')
# # columns = Columns(db)
# # first = columns.get_column('name')
# # first.add_new_row('name', 'Kendall Jenner', 1)
# # first.add_new_row('age', 15, 1)
# # first.add_new_row('name', 'Kylie', 2)
# # print(columns.as_records)
# db.update('name', 'Kendall')
# db.update('age', 14)
# db.update('country', 1)
# db2.update('name', 'France')
# # print(db)
# # print(db2)
# print(db.get_related_item(1, db2))


a = Columns(db)
c = a.get_column('name')
c.add_new_row('name', 'Kendall')
