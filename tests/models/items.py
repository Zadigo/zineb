from zineb.models.datastructure import Model
from zineb.models import fields


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
    url = fields.UrlField()


class ExampleModel2(Model):
    value = fields.CharField()