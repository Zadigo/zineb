from zineb.models.datastructure import Model
from zineb.models import fields

def auto_detect_date(d):
    if '.' in d:
        return d.replace('.', '-')
    return d

class TestModel(Model):
    dob = fields.FunctionField(auto_detect_date, output_field=fields.DateField('%d-%M-%Y'))

model = TestModel()
model.add_value('dob', '01.01.2021')
model.save(filename='test_file')
