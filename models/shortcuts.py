from zineb.models.datastructure import Model
from zineb.models.fields import Field


class InlineModel:
    """Shortcut to create a model rapidly"""
    
    def __call__(self, name, fields=[], model=None):
        model = model or Model
        attrs = {}
        for item in fields:
            name, value = item
            if not isinstance(value, Field):
                raise ValueError('Field should be an instance of Field')
            attrs[name] = value

        attrs['__qualname__'] = name.title()
        attrs['__name__ '] = name.title()
        # TODO: Update __doc__ and __module__ path to
        # point to the model's project
        instance = type(name.title(), (model,), dict(attrs))
        return instance()

# TODO: Create test for inline_model

inline_model = InlineModel()
