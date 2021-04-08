# from zineb.models import operationals


# class Operations(BaseOperations):
#     operations = [
#         operationals.Create(
#             name='MyModel',
#             fields=[
#                 ('name', fields.CharField())
#             ],
#             options={
#                 'ordering': []
#             }
#         ),
#     ]


class BaseOperations:
    operations = []

    def create_operation(self, model:type):
        model_name = model.__class__.__name__
        loaded_model = model()
        fields = model._fields.cached_fields


class Create:
    def __init__(self):
        pass
