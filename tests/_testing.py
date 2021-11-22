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
# s.as_csv()


from zineb.models import fields

u = fields.JsonField()
u.resolve({'a': 1})
print(u._cached_result)
