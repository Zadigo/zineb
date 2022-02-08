from zineb.models.datastructure import Model
from zineb.models import fields

# Implement your models here

class SimpleModel(Model):
    url = fields.UrlField()
    