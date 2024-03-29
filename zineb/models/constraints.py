from collections import Counter

from zineb.exceptions import ConstraintError, FieldError


class BaseConstraint:
    def __init__(self, fields, name, condition=None):
        self.name = name
        self.model = None
        self._data_container = None
        self.constrained_fields = list(fields)
        self.condition = condition

    def __repr__(self):
        return f'<{self.__class__.__name__}[{self.model._meta.name}{self.constrained_fields}]>'

    def __call__(self, value_to_check):
        if self.model is None:
            raise ValueError('Constraint is not attached to any model')

        errors = []
        counter = Counter()
        if len(self.constrained_fields) == 1:
            field = self.constrained_fields[-1]
            counter.update(self._data_container.get_container(field))
            
            element_count = counter.get(value_to_check, 0)
            if element_count == 1:
                errors.extend(
                    [(field, ConstraintError(self.model._meta.model_name, self.name))]
                )
        else:
            for field in self.constrained_fields:
                counter.update(self._data_container.get_container(field))

            element_count = counter.get(value_to_check, 0)
            if element_count == 1:
                errors.extend(
                    [(self.constrained_fields, ConstraintError(self.model._meta.model_name, self.name))]
                )

        if self.condition is not None:
            result = self.condition(value_to_check)
            if not result:
                errors.extend(
                    [(field, ConstraintError(self.model._meta.model_name, self.name))]
                )

        return errors

    def update_model_options(self, model):
        self.model = model
        self._data_container = model._data_container

        # TODO: When the fields are not in the model
        # raise an error. Only fields within the model
        # are allowed
        # errors = []
        # for field in self.constrained_fields:
        #     if not model._meta.field_exists(field):
        #         errors.extend([FieldError(field, model._meta.fields, self.model.name)])

        # if errors:
        #     raise ExceptionGroup('', errors) 


class UniqueConstraint(BaseConstraint):
    """Forces the model to skip the
    saving process when a value is found in
    the existing dataset

    Example
    -------

    >>> Class MyModel(Model):
            class Meta:
                constraints = [
                    UniqueConstraint(fields=[...], name=...)
                ]
    """
