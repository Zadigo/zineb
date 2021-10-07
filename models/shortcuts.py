from typing import Type

from zineb.models.datastructure import Model
from zineb.models.fields import Field


class InlineModel:
    def __call__(self, name: str, fields: list = [], model: Type = None):
        model = model or Model
        attrs = set()
        for field in fields:
            for key, value in field.items():
                if not isinstance(value, Field):
                    raise ValueError('Field should be an instance of Field')
                attrs.add((key, value))

        instance = type(name, (model,), dict(attrs))
        instance.__qualname__ = name.lower().title()
        instance.__name__ = name.lower().title()
        setattr(instance, 'inline_model', True)
        return instance

inline_model = InlineModel()
