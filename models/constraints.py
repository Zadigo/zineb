from zineb.exceptions import FieldError
from zineb.exceptions import ConstraintError
from collections import Counter, defaultdict

class BaseConstraint:
    def __init__(self, fields, name, condition=None):
        self.name = name
        self.model = None
        self._data_container = None
        self.constrained_fields = list(fields)
        # self.condition = condition
        
    def __repr__(self):
        return f'<{self.__class__.__name__}[{self.model._meta.model_name}{self.constrained_fields}]>'
    
    def __call__(self, raise_exception=False):
        errors = []
        # Create a counter for all the values
        # present in a field on the database
        most_common = defaultdict(list)
        for field in self.constrained_fields:
            values = self._data_container.get_container(field)
            counter = Counter(values)
            most_common[field] = counter
            
        for field, counter in most_common.items():
            count = counter.most_common()
            for item in    count:
                value, count = item
                # Since we're creating new rows in the SmartDict
                # that could be None, we have to skip None which
                # would obviously mean a common value
                if value is None:
                    continue
                
                if count > 1:
                    errors.extend([(field, ConstraintError(self.model._meta.model_name, self.name))])
                
        if errors and raise_exception:
            raise ValueError(*errors)
        
        return errors
        
    def prepare(self):
        try:
            self._data_container = self.model._data_container
        except:
            raise ValueError('Instance is not a Model instance')
        
        for field in self.constrained_fields:
            if not self.model._meta.has_field(field):
                raise ValueError('Field is not on model')

                
class UniqueConstraint(BaseConstraint):
    """Raises an error when a constraint is found
    on a given model"""
    
    def __call__(self, raise_exception=True):
        return super().__call__(raise_exception=raise_exception)
    
        
class CheckConstraint(BaseConstraint):
    """Prevents the addition of a given value
    in the data container if a constraint is
    found without raising an error"""
    
    def __call__(self):
        errors = super().__call__()
        for error in errors:
            yield error[0]
    


# from zineb.models.datastructure import Model
# from zineb.models import fields
# class TestModel(Model):
#     name = fields.CharField()
#     surname = fields.NameField()

# model = TestModel()
# model.add_value('name', 'Kendall')
# model.add_value('name', 'Kendall')
# constraint = UniqueConstraint(['name', 'surname'], 'unique_name_and_surname')
# constraint.model = model
# constraint.prepare()
# print(constraint())
