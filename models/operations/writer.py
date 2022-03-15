from io import FileIO

class OperationWriter:
    def __init__(self, model):
        self.model = model
        
        template = """
        from zineb.models import fields
        from zineb.models.operations import actions
        from zineb.models.operations.base import Operations
        
        
        class Operation(Operations):
            model = 'some_model'
            actions = [
                {actions}
            ]
        """
        template.format(actions='something')
        with open('./models/operations/test_operations/002_test.py', mode='wb') as f:
            # template = template.format(actions='test')
            # template = template.strip()
            # f.write(template.encode('utf-8'))
            lines = [
                'from zineb.models import fields', '\n', 
                'from zineb.models.operations import actions', '\n',
                'from zineb.models.operations.base import Operations', '\n'
            ]
            data = [line.encode('utf-8') for line in lines]
            f.writelines(data)
            
            klass = """
            class Operation(Operations):
                model = '{name}'
                actions = [
                    {actions}
                ]
            """
            name, fields = self.deconstruct_model()
            representations = self.construct_fields_representation(fields)
            klass = klass.format(name=name, actions=', '.join(representations))
            f.write(klass.encode('utf-8'))
            
    def deconstruct_model(self):
        model_meta = self.model._meta
        fields = [(name, field) for name, field in model_meta.cached_fields.items()]
        return model_meta.model_name, fields
        
    def construct_fields_representation(self, fields):
        for _, field in fields:
            options = []
            max_length = getattr(field, 'max_length', None)
            if max_length is not None:
                options.append(f"max_length={max_length}")
            options_as_string = ', '.join(options)
            yield 'fields.{name}({options})'.format(name=str(field.__class__.__name__), options=options_as_string)
            
    def construct_action(self, name, value, action_name, field):
        if name == 'add_value':
            template = "actions.AddValue('add_value', {value}, {action_name}, {field})"
        return template.format(value=value, action_name=action_name, field=field)

from zineb.models.datastructure import Model
from zineb.models import fields

class TestModel(Model):
    name = fields.CharField(max_length=50)

w = OperationWriter(model=TestModel())
