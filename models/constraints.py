from zineb.exceptions import ConstraintError

class BaseConstraint:
    def __init__(self, fields, name, condition=None):
        self.name = name
        self._data_container = None
        self.constrained_fields = list(fields)
        self.condition = condition
        self.values = {}
        self.unique_together = []
        self.unique = []
        
    def __repr__(self):
        return f'<{self.__class__.__name__} for {self.model}>'
        
    def prepare(self):
        if len(self.constrained_fields) == 1:
            self.unique.extend(self.values[field])
        else:
            for field in self.constrained_fields:
                container = self.values[field]
                self.unique_together.append(container)

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
        
        return all(truth_array)


class UniqueConstraint(BaseConstraint):
    """Raises an error when a constraint is found
    on a given model"""

    def check_constraint(self, value_to_check):
        result = super().check_constraint(value_to_check)
        if not result:
            raise ConstraintError()
        return result
        
        
class CheckConstraint(BaseConstraint):
    """Prevents the addition of a given value
    in the data container if a constraint is
    found without raising an error"""
    
    def check_constraint(self, value_to_check):
        result = super().check_constraint(value_to_check)
        return_data = {}
        if not result:
            for field in self.constrained_fields:
                return_data[field] = self._data_container[field]
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




# constraint = UniqueConstraint('name', 'surname', condition=lambda x: x == 15)
# constraint.values = {'name': ['Kendall'], 'surname': ['Jenner']}
# constraint.prepare()
# constraint.check_constraint('Kendall')
# print(constraint)



# class BaseConditions:
#     pass
    

# class Q(BaseConditions):
#     """A function that can query a value in
#     a given model and return the result of
#     of the condition"""
#     def __init__(self, *args, negated=False, **kwargs):
#         pass


# q = Q(name__eq='Kendall', surname__eq='Jenner')
