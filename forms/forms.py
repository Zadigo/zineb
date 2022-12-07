from typing import OrderedDict

from zineb.http.request import FormRequest
from zineb.models import fields
from zineb.models.fields import Field
from zineb.utils.formatting import LazyFormat


class BaseForm(type):
    def __new__(cls, name, bases, attrs):
        create_new = super().__new__

        new_attrs = {}

        for key, value in attrs.items():
            if hasattr(value, 'update_form_fields'):
                new_attrs.update({key: value})

        # declared_fields = set()
        # for key, field_obj in attrs.items():
        #     if isinstance(field_obj, Field):
        #         field_obj.upd
        #         declared_fields.add((key, field_obj))

        # if declared_fields:
        #     fields = OrderedDict(list(declared_fields))
        #     attrs['_fields'] = fields
        #     attrs['_true_fields'] = list(fields.values())
        #     attrs['_field_names'] = list(fields.keys())

        # If the user creates a function of
        # type clean_[field name] then we
        # then we need to detect these
        # functions in order to pass

        # field_functions = [f'clean_{field}' for field in fields.keys()]
        # for key, func in attrs.items():
        #     if key in field_functions:
        #         new_class.update(key, None)

        new_class = create_new(cls, name, bases, attrs)
        return new_class
            

class Form(metaclass=BaseForm):
    def __init__(self, data):
        self.validated_data = {}
        self.data_fields = []

        if hasattr(self, '_field_names'):
            for key in data.keys():
                if key not in self._field_names:
                    raise ValueError('Field is not present on the form')
            self.data_fields = data.keys()
            self.full_clean(data)

    def __call__(self, data: dict={}):
        self.__init__(data=data)
        return self.validated_data

    def full_clean(self, data):
        for name in self.data_fields:
            field_obj = self._fields[name]
            value_to_resolve = data[name]

            custom_func = f'clean_{name}'
            func = getattr(self, custom_func, None)
            if func is not None:
                value_to_resolve = func(value_to_resolve)
                if value_to_resolve is None:
                    raise ValueError(LazyFormat('Custom function {func} '
                    'should return a value', func=custom_func))

            field_obj.resolve(value_to_resolve)
            self.validated_data[name] = field_obj._cached_result
        self.clean(self.validated_data)

    def clean(self, validated_data):
        pass


# class TestForm(Form):
#     name = fields.CharField()


# test = TestForm(data={'name': 'Kendall'})
# request = FormRequest('http://example.com', test)

# print(test.validated_data)

form = Form({'name': 'Kendall'})
