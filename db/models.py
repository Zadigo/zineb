from typing import Any
from zineb.db.schema import SchemaEditor
from zineb.db.fields import Field
from zineb.db import get_database_backend
from collections import OrderedDict

class Manager:
    _db_instance = None
    _attached_model = None
    _attached_to_model_name = None

    @classmethod
    def as_manager(cls, model=None):
        instance = cls()
        instance._attached_model = model
        return instance


class BaseModel(type):
    def __new__(cls, name, attrs, bases):
        create_new = super().__new__
        descriptor = []
        obj_dict = cls.__dict__
        for key, value in obj_dict.items():
            if isinstance(value, Field):
                descriptor.append((key, value))
        klass = create_new(cls, name, attrs, bases)
        setattr(klass, '_fields', OrderedDict(descriptor))
        setattr(klass, '_connection', get_database_backend())
        return klass


class Model(metaclass=BaseModel):
    _fields = []
    related_fields = []

    _default_manager = Manager
    manager = None

    _connection = None
    _schema = SchemaEditor

    def __init__(self):
        self.model_name = self._pluralize(self.__class__.__name__)
        self._default_manager.as_manager(model=self)
        setattr(self._default_manager, '_attached_to_model', self.model_name)
        setattr(self._default_manager, '_attached_model', self)

    def __getattr__(self, name):
        if name == '_connection':
            _connection = getattr(self, '_connection')
            if _connection is None:
                self._connection = get_database_backend()
        return super().__getattr__(name)

    def __setattr__(self, name: str, value: Any):
        if name == 'manager':
            if not issubclass(value, Manager):
                raise TypeError('Managers of the model should be an instance of the Manager class')
        return super().__setattr__(name, value)

    @staticmethod
    def _pluralize(name: str):
        if name.endswith('s'):
            return name
        return f'{name}s'
