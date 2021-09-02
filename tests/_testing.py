# from zineb.models.datastructure import DataContainers

# container = DataContainers.as_container('name', 'age')

# container.update('name', 'Kendall')

# container.update('name', 'Kylie')
# container.update('age', 22)

# container.update('age', 26)

# print(container.values)

from zineb.models.expressions import When
from zineb.models.datastructure import Model
from zineb.models import fields
from zineb.models.expressions import Substract

class TestModel(Model):
    age = fields.IntegerField()
    age2 = fields.IntegerField()

model = TestModel()
print(model)
