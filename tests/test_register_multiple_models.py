from zineb.models import fields
from zineb.models.datastructure import Model

# TODO: Resolve the MRO for models that are
# subclassed. What we want to do is collide 
# the fields from super class in the subclass
# and act as if they are one

class ModelA(Model):
    name = fields.CharField()

    class Meta:
        template_model = True


class ModelB(ModelA):
    surname = fields.CharField(max_length=10)


# TODO: When trying to register multiple models,
# ModelExistsError gets raised. For example,
# model C will raise an error because model A
# is already registered


class ModelC(Model):
    height = fields.CharField()


print(ModelB._meta)
