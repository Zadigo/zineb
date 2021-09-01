# from zineb.app import Options


# options = Options(domains=['http://example.com'])
# print(options.check_url_domain('example.com'))

# cache = {'a': [], 'b': []}

# def add_value(name, value):
#     cache[name].append(value)
#     lengths = [[key, len(values)] for key, values in cache.items()]
#     for i in range(0, len(lengths)):
#         x = i + 1
#         if x >= len(lengths):
#             break
#         if lengths[x][1] < lengths[i][1]:
#             cache[lengths[x][0]].append(None)
#         if lengths[x][1] == lengths[i][1]:
#             cache[lengths[i][0]].insert(x, value)

# add_value('a', 1)
# add_value('a', 2)
# add_value('b', 3)
# print(cache)


from typing import Type, Union
from zineb.models.datastructure import Model
from zineb.models import fields
from zineb import exceptions

class RelatedField:
    field_name = None

    def __init__(self, model: Union[Type, str], related_name: str=None):
        self.model = None
        self.related_name = related_name

        if isinstance(model, str):
            pass

        if isinstance(model, type):
            pass

        self.field_name = self.related_name or self.field_name

        setattr(self, self.field_name, self.model)

    def add_value(self):
            self.model.add_value()
    

def name_validator(value):
    if value == 'Kendall':
        raise exceptions.ValidationError('Name is not valid')
    return value

class Competitions(Model):
    name = fields.NameField()


class Player(Model):
    name = fields.NameField(validators=[name_validator])
    surnames = RelatedField(Competitions)
