from models.fields import ArrayField, CharField
from zineb.models.fields import EmailField

field = ArrayField(output_field=CharField())
field.resolve("[1, 2, 3, {'a': 1}]")
print(field._cached_result)
