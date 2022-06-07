from zineb.exceptions import FieldError
from zineb.exceptions import ConstraintError
from collections import Counter, defaultdict


class BaseConstraint:
    def __init__(self, fields, name, condition=None):
        self.name = name
        self.model = None
        self._data_container = None
        self.constrained_fields = list(fields)
        self.condition = condition
        self.values = defaultdict(list)
        self.unique = []
        self.unique_together = []
        
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
       
    def prepare(self, model):
        # FIXME: Don't know what self.values serves to.
        # Apparently it implements the values for each
        # field on a dict
        self._data_container = model._data_container
        
        if len(self.constrained_fields) == 1:
            self.unique.extend(self.values[field])
        else:
            for field in self.constrained_fields:
                container = self.values[field]
                self.unique_together.append(container)
                
        model._meta.add_constraint(self.name)

    def check_constraint(self, value_to_check):
        # If we have a unique together, it means that
        # two fields have to be both unique together
        truth_array = []
        if self.unique_together:
            results = map(lambda x: value_to_check in x, self.unique_together)
            truth_array.extend(list(results))
            
        if self.unique:
            result = value_to_check in self.unique
            truth_array.append(result)
            
        if self.condition is not None:
            pass
        
        
class UniqueConstraint(BaseConstraint):
    """Raises an error when a constraint is found
    on a given model"""
    
    def __call__(self, raise_exception=True):
        return super().__call__(raise_exception=raise_exception)
    
        
class CheckConstraint(BaseConstraint):
    """Prevents the addition of a given value
    in the data container if a constraint is
    found without raising an error"""
    
    def check_constraint(self, value_to_check):
        result = super().check_constraint(value_to_check)
        return_data = {}
        if not result:
            for field in self.constrained_fields:
                # FIXME: Return the container without the
                # value that was constrained
                return_data[field] = self._data_container[field]
                # return_data[field] = self.values[field]
        return return_data


# @total_ordering
# class V:
#     def __init__(self, value):
#         self.value = value

#     def __repr__(self):
#         return f'{self.__class__.__name__}([{self.value}])'

#     def __eq__(self, obj):
#         return obj == self.value

#     def __gt__(self, obj):
#         obj = self.convert_to_string(obj)
#         return len(self.value) > obj

#     def __contains__(self, obj):
#         obj = self.convert_to_string(obj)
#         return self.value in obj

#     def convert_to_string(self, value):
#         if isinstance(value, (int, float)):
#             return str(value)
#         return value


# constraint = CheckConstraint(['name', 'surname'], 'unique_name', condition=lambda x: x == 15)
# constraint = UniqueConstraint(['name', 'surname'], 'unique_name', condition=lambda x: x == 15)
# constraint.values = {'name': ['Kendall'], 'surname': ['Jenner']}
# constraint.prepare()
# print(constraint.check_constraint('Kendall'))
# print(constraint)



# class BaseConditions:
#     pass

  

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
