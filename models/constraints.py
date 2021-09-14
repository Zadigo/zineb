from zineb.models.datastructure import Model
from zineb.exceptions import ModelConstrainError

class BaseConstraint:
    def __init__(self, *fields, tag: str=None, condition=None, raise_exception: bool=False):
        if not fields:
            raise ValueError('At least one field is required.')

        self.fields = set(fields)
        self.tag = tag
        self.raise_exception = False

    def _check_constraint(self, model, value):
        if not isinstance(model, Model):
            raise TypeError('model should be an instance of zineb.models.Model.')

        model._fields.has_fields(*self.fields, raise_exception=True)

        for name in self.fields:
            container = model._cached_result.get_container(name)
            if value in container:
                if self.raise_exception:
                    raise ModelConstrainError(name, value)
                else:
                    value = None
            model._cached_result.update(name, value)
    

class UniqueConstraint(BaseConstraint):
    """
    Overrides the default update with a unique constraint
    that writes a value only it is not present in one of
    the contains specified by the fields
    """
    def __repr__(self):
        return (f"{self.__class__.__name__}"
        "(fields={''.join(self.fields)})")
