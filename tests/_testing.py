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


from zineb.models.transactions import transaction, atomic
from zineb.tests.models import items
from zineb.models.datastructure import Model

# with transaction(items.SimpleModel()) as t:
#     t.model.add_value('name', 'Kendall')
#     s1 = t.savepoint()
#     t.rollback()

# class Google:
#     @atomic(items.SimpleModel)
#     def start(self, response, request, transaction, **kwargs):
#         print(transaction)


# g = Google()
# g.start(request='a', response='b')
