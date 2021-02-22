from zineb.models.fields import DecimalField, Field, IntegerField, NameField, TextField, UrlField, CharField
from zineb.models.datastructure import Model


class SomeModel(Model):
    name = CharField()
    age = IntegerField(min_value=18)


player = SomeModel()
player.add_value('name', 'Kendall')
player.add_value('age', 9)
print(player)
# field = CharField()
# print(field, isinstance(field, Field), issubclass(field.__class__, Field))
