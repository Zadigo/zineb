from zineb.models import fields
from zineb.models.constraints import CheckConstraint
from zineb.models.datastructure import Model


def simple_validator(value):
    return value    


class BareModel(Model):
    age = fields.IntegerField()


class AgeModel(Model):
    age = fields.AgeField()
    

class SimpleModel(Model):
    name = fields.CharField()
    date_of_birth = fields.DateField()
    age = fields.AgeField()


class ModelWithValidator(Model):
    height = fields.IntegerField(validators=[simple_validator])


class DateModel(Model):
    date_of_birth = fields.DateField()


class ModelWithMeta(Model):
    name = fields.CharField()

    class Meta:
        ordering = ['name']


class ModelWithInvalidMeta(Model):
    class Meta:
        ordering = ['name']


class SubclassedModel(BareModel):
    pass


class CalculatedModel(Model):
    age = fields.IntegerField()


class ExampleModel(Model):
    url = fields.URLField()


class ExampleModel2(Model):
    value = fields.CharField()


<<<<<<< HEAD
class ConstrainedModel(Model):
    name = fields.CharField()
    
    class Meta:
        constraints = [
            CheckConstraint('my_contraint', 'name')
        ]
# c = ConstrainedModel()
# print(c._meta.cached_options)
=======
class BasicModel(Model):
    name = fields.NameField()
    age = fields.IntegerField()


class SortedModel(Model):
    name = fields.NameField()
    age = fields.IntegerField()
    height = fields.EmailField()
    
    
class ComplicatedModel(Model):
    name = fields.NameField()
    year_of_birth = fields.IntegerField()
    zip_code = fields.IntegerField()
    current_balance = fields.IntegerField()


class RelatedModel2(Model):
    surname = fields.CharField()
    
    
class RelatedModel1(Model):
    surname = fields.RelatedModel(RelatedModel2)
    age = fields.IntegerField()
    
>>>>>>> develop
