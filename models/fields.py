import ast
import datetime
import json
import re
from typing import Any, Callable, List, Tuple, Union

from bs4.element import Tag as beautiful_soup_tag
from w3lib import html
from w3lib.url import canonicalize_url, safe_download_url
from zineb.exceptions import ValidationError
from zineb.models import validators as model_validators
from zineb.settings import settings
from zineb.utils.characters import deep_clean
from zineb.utils.conversion import convert_to_type, detect_object_in_string
from zineb.utils.encoders import DefaultJsonEncoder
from zineb.utils.formatting import LazyFormat
from zineb.utils.images import download_image_from_url


class Empty:
    """
    Class that represents '' as a Python object.
    These string are not considered None in Python
    but do no have any value
    """


class Field:
    """Base class for all fields """

    name = None
    _cached_result = None
    _default_validators = []
    _dtype = str

    def __init__(self, max_length: int=None, null: bool=True, 
                 default: Union[str, int, float]=None, validators=[]):
        self._meta_attributes = {'field_name': None}

        self.max_length = max_length
        self.null = null

        self._validators = set(validators)
        if self._default_validators:
            self._validators = (
                self._validators | 
                set(self._default_validators)
            )

        self.default = default

        # Be careful here, the problem is each
        # time the field is used, a validator
        # is added for each new value which
        # creates an array containing the same
        # validators
        if self.max_length is not None:
            self._validators.add(model_validators.MaxLengthValidator(self.max_length))

        if not self.null:
            self._validators.add(model_validators.validate_is_not_null)

    def _bind(self, field_name, model=None):
        """Bind the field's name registered 
        on the model to this field instance"""
        self._meta_attributes.update(field_name=field_name)
        current_model = self._meta_attributes.get('model', None)
        if current_model is None and model is not None:
            self._meta_attributes['model'] = model

    def _true_value_or_default(self, value):
        if self.default is not None and value is None:
            return self.default
        
        if self.default is not None and value == Empty:
            return self.default

        return value

    def _to_python_object(self, value: Any, use_dtype=None):
        """
        Returns the true python representation
        of a given value
        """
        dtype = use_dtype or self._dtype
        return convert_to_type(value, t=dtype, field_name=self._meta_attributes.get('field_name'))

    def _run_validation(self, value):
        # Default values should be validated
        # too ? Otherwise the user might enter
        # anykind of none validated value ??
        value = self._true_value_or_default(value)

        # If the value is None, makes no sense
        # to continue the validation, just return
        # None instead
        if value is None:
            return None

        validator_return_value = None
        for validator in self._validators:
            if not callable(validator):
                raise TypeError('A Validator should be a callable.')
            try:
                if validator_return_value is None:
                    validator_return_value = validator(value)
                else:
                    validator_return_value = validator(validator_return_value)
            except:
                message = ("A validation error occured on "
                "field '{name}' with value '{value}'.")
                raise Exception(
                    LazyFormat(message, name=self._meta_attributes.get('field_name'), value=value)
                )
        if self._validators:
            return validator_return_value
        return value

    def _check_emptiness(self, value):
        """
        Deals with true empty values e.g. '' that
        are factually None but get passed
        around as containing data
        
        The Empty class is the pythonic representation
        for these kinds of strings
        """
        value = Empty
        result = self._run_validation(value)
        self._cached_result = result
        return self._cached_result

    def _simple_resolve(self, clean_value, convert=False, dtype=None):
        """
        A value resolution method that only runs validations.

        This definition is useful for example for revalidating the end
        result value of a field that does not require any cleaning
        or normalization.

        NOTE: This should ONLY be used internally and
        not on incoming data from the web since it does
        not apply any kind of formatting (spaces, escape
        characters or HTML tags)
        """
        self._cached_result = self._run_validation(clean_value)
        
        if convert:
            if dtype is None:
                dtype = self._dtype
            self._cached_result = self._to_python_object(self._cached_result)

        return self._cached_result

    def resolve(self, value: Any, convert: bool=False, dtype: Any=None):
        """
        This is the main resolution function that deals with
        making and incoming scrapped value from the internet
        as normal and usabled as possible by the framework

        The value can also be converted to it's true 
        Pythonic representation

        NOTE: Subclasses should implement their own resolve function
        and/or call super().resolve() to benefit from the cleaning
        and normalizing logic
        """
        if value == '':
            return self._check_emptiness(value)

        true_value = None
        if isinstance(value, beautiful_soup_tag):
            try:
                true_value = value.text
            except AttributeError:
                raise AttributeError(
                    LazyFormat("Could not get attribute text from '{value}'.", value=true_value)
                )

        # There might be a case where a None
        # value slides in and breaks everything.
        # We should just run th validation process
        # in that case and avoid cleaning anything.
        if value is None:
            return self._run_validation(value)

        if not isinstance(value, (str, int, float)):
            raise ValueError(LazyFormat('{value} should be a string, '
            'an integer or a float.', value=value))
        
        # To make things easier, we'll just
        # be dealing with a string even though
        # its true Python representation is not
        true_value = str(value)

        if '>' in true_value or '<' in true_value:
            true_value = html.remove_tags(value)

        clean_value = deep_clean(true_value)

        return self._simple_resolve(clean_value, convert=convert, dtype=dtype)
            

class CharField(Field):
    name = 'char'

    def resolve(self, value):
        return super().resolve(value, convert=True)


class TextField(CharField):
    name = 'text'

    def __init__(self, max_length: int=500, **kwargs):
        super().__init__(max_length=max_length, **kwargs)


class NameField(CharField):    
    name = 'name'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def resolve(self, value):
        super().resolve(value)
        self._cached_result = self._cached_result.lower().title()


class EmailField(Field):
    _default_validators = [model_validators.validate_email]

    def __init__(self, limit_to_domains: Union[List[str], Tuple[str]] = [],
                 null: bool=False, default: Any=None, validators: list=[]):
        super().__init__(null=null, default=default, validators=validators)
        self.limit_to_domains = limit_to_domains

    def _check_domain(self, domain):
        if self.limit_to_domains:
            if domain not in self.limit_to_domains:
                raise ValidationError(f'{domain} is not in valid domains.')

    def resolve(self, value):
        result = super().resolve(value)
        if result is not None or result != Empty:
            _, domain = value.split('@')
            self._check_domain(domain)


class UrlField(Field):
    name = 'url'
    _default_validators = [model_validators.validate_url]

    def resolve(self, url):
        result = super().resolve(url)
        if result is not None:
            result = safe_download_url(canonicalize_url(url))


class ImageField(UrlField):
    """
    Field for representing an image url in a model

    Parameters
    ----------

        - download (bool, optional): download the image. Defaults to False
        - as_thumbnail (bool, optional): download as a thumnail. Defaults to False
        - download_to (str, optional): download image to a specific path. Defaults to None
    """
    name = 'image'

    def __init__(self, download: bool=False, as_thumnail: bool=False, download_to: str=None):
        super().__init__()

        self.download = download
        self.as_thumbnail = as_thumnail
        # self.image_data = None
        # self.metadata = {}
        self.download_to = download_to

    def resolve(self, url):
        super().resolve(url)
        
        

        if self.download:
            download_image_from_url(
                self._cached_result,
                download_to=self.download_to,
                as_thumbnail=self.as_thumbnail
            )


class IntegerField(Field):
    name = 'integer'
    _dtype = int

    def __init__(self, default: Any=None, min_value: int=None, 
                 max_value: int=None, validators: list=[]):
        super().__init__(default=default, validators=validators)

        if min_value is not None:
            self._validators.add(model_validators.MinLengthValidator(min_value))

        if max_value is not None:
            self._validators.add(model_validators.MaxLengthValidator(max_value))

    def resolve(self, value):
        super().resolve(value, convert=True)


class DecimalField(IntegerField):
    name = 'decimal'
    _dtype = float


class DateFieldsMixin:
    def __init__(self, date_format: str=None, default: Any=None):
        super().__init__(default=default)

        self.date_parser = datetime.datetime.strptime

        formats = set(getattr(settings, 'DEFAULT_DATE_FORMATS'))
        formats.add(date_format)
        self.date_formats = formats

    def _to_python_object(self, result: str):
        for date_format in self.date_formats:
            try:
                d = self.date_parser(result, date_format)
            except:
                d = None
            else:
                if d:
                    break
        
        if d is None:
            message = LazyFormat("Could not find a valid format for "
            "date '{d}' on field '{name}'.", d=result, name=self._meta_attributes.get('field_name'))
            raise ValidationError(message)
        return d.date()


class DateField(DateFieldsMixin, Field):
    name = 'date'

    def resolve(self, date: str):        
        super().resolve(date, convert=True)


class AgeField(DateFieldsMixin, Field):
    name = 'age'
    _dtype = int

    def __init__(self, date_format: str=None, default: Any = None):
        super().__init__(date_format=date_format, default=default)
        self._cached_date = None
        
    def _substract(self) -> int:
        current_date = datetime.datetime.now()
        return current_date.year - self._cached_date.year

    def resolve(self, date: str):
        result = super().resolve(date)
        self._cached_date = self._to_python_object(self._cached_result)
        self._cached_result = self._substract()


class FunctionField(Field):
    """
    Field that resolves a value by passing it through
    different custom methods
    """
    name = 'function'

    def __init__(self, *methods: Callable[[Any], Any], output_field: Field = None, 
                 default: Any = None, validators: list = []):
        super().__init__(default=default, validators=validators)

        if not methods:
            raise ValueError('FunctionField expects at least on method.')

        self.methods = []
        self.output_field = output_field

        if output_field is not None:
            if not isinstance(output_field, Field):
                raise TypeError(("The output field should be one of "
                        "zineb.models.fields types and should be "
                        "instanciated e.g. FunctionField(output_field=CharField())"))
        else:
            self.output_field = CharField()
        
        incorrect_elements = []
        for method in methods:
            if not callable(method):
                incorrect_elements.append(method)
            self.methods.append(method)

        if incorrect_elements:
            raise TypeError(LazyFormat('You should provide a list of '
            'callables. Got: {incorrect_elements}', incorrect_elements=incorrect_elements))

    def resolve(self, value):
        super().resolve(value, convert=True)

        new_result = None
        for method in self.methods:
            if new_result is None:
                new_result = method(self._cached_result)
            else:
                new_result = method(new_result)

        self.output_field._simple_resolve(new_result, convert=True)
        self._cached_result = self.output_field._cached_result


class MappingFieldMixin:
    def resolve(self, value):
        if isinstance(value, str):
            return detect_object_in_string(super().resolve(value))
        return value


class ListField(MappingFieldMixin, Field):
    name = 'list'
    _dtype = list

    def __init__(self, default: Any = None, 
                 validators = []):
        super().__init__(default=default, validators=validators)

    def resolve(self, value):
        result = super().resolve(value)
        self._cached_result = self._to_python_object(result)


class JsonField(MappingFieldMixin, Field):
    name = 'json'
    _dtype = dict

    def __init__(self, validators: list=[]):
        super().__init__(validators=validators)

    def resolve(self, value):
        result = super().resolve(value)

        if not isinstance(result, dict):
            raise ValueError(LazyFormat("{class_name} should receive "
            "a dict as value.", class_name=self.__class__.__name__))

        self._cached_result = detect_object_in_string(
            json.dumps(result, cls=DefaultJsonEncoder)
        )


class CommaSeperatedField(Field):
    name = 'comma_separated'

    def __init__(self, max_length: int = None):
        super().__init__(max_length=max_length)

    def resolve(self, values: List[Any]):
        if isinstance(values, str):
            values = detect_object_in_string(values)

        if not isinstance(values, (list, tuple)):
            raise TypeError('The values parameter should be of type str, list or tuple.')
        
        container = ','.join(map(lambda x: str(x), values))
        self._cached_result = self._to_python_object(container)


class RegexField(Field):
    name = 'regex'

    def __init__(self, pattern: str, group: int = 0, output_field: Field=None, **kwargs):
        self.pattern = re.compile(pattern)
        self.group = group
        self.output_field = output_field
        super().__init__(**kwargs)

    def resolve(self, value: str):
        value = self._run_validation(value)
        try:
            # If the value is None, this raises and
            # error, hence the try-catch function
            regexed_value = self.pattern.search(value)
        except TypeError:
            self._cached_result = None
        else:
            if regexed_value:
                result = regexed_value.group(self.group)

                if self.output_field is not None:
                    if not isinstance(self.output_field, Field):
                        raise TypeError((f"Output field should be a instance of " 
                        "zineb.fields.Field. Got: {self.output_field}"))
                    self._cached_result = self.output_field.resolve(result)
                else:
                    self._cached_result = result


class BooleanField(Field):
    name = 'boolean'
    _dtype = bool
    
    REP_TRUE = ['True', 'true', '1', 
                'ON', 'On', 'on', True]

    REP_FALSE = ['False', 'false', '0', 
                 'OFF', 'Off', 'off', False]

    def __init__(self, default: Any=None, null: bool=True):
        super().__init__(null=null, default=default)

    def _true_value_or_default(self, value):
        if isinstance(self.default, bool) and (value is None or value == Empty):
            return self.default
        return super()._true_value_or_default(value)

    def resolve(self, value: Any):
        if value in self.REP_TRUE:
            self._cached_result = True
        elif value in self.REP_FALSE:
            self._cached_result = False
        else:
            if value == '':
                value = Empty
            result = self._run_validation(value)              

            if not isinstance(result, bool) and not self.null:
                raise ValueError('BooleanField accepts booleans as value.')
            self._cached_result = result


class Value:
    """
    A simple field that can be used to represent a value
    extracted frome the internet

    Parameters
    ----------

        - value (Any): a value from the internet. Defaults to None
        - field_name (str): field's name. Defaults to None.
    """
    result = None

    def __init__(self, value: Any, field_name: str=None):
        self.result = value
        self.field_name = field_name

    def __str__(self):
        return self.result

    def __repr__(self):
        return f"{self.__class__.__name__}({self.result})"

    def __setattr__(self, name, value):
        if name == 'result':
            value = deep_clean(value)
        return super().__setattr__(name, value)
        