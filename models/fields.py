import ast
import datetime
import json
import re
from typing import Any, Callable, List, Tuple, Union

import numpy
import pandas
import pytz
from bs4.element import Tag as beautiful_soup_tag
from w3lib import html
from w3lib.url import canonicalize_url, safe_download_url
from zineb.http.request import HTTPRequest
from zineb.models import validators as model_validators
from zineb.utils._html import deep_clean
from zineb.utils.images import download_image_from_url

Number = Union[int, float]



class Field:
    """
    This is the base class for all field classes

    Raises:
        TypeError: [description]
        an: [description]
        TypeError: [description]

    Returns:
        [type]: [description]
    """

    name = None
    _cached_result = None
    _default_validators = []
    _dtype = numpy.str

    def __init__(self, max_length: int=None, null=True, default: Any = None, 
                 validators = []):
        self.max_length = max_length
        self.null = null
        # self._validators = validators

        # if self._default_validators:
        #     self._validators = self._validators + self._default_validators

        self._validators = set(validators)
        if self._default_validators:
            self._validators = (
                self._validators | 
                set(self._default_validators)
            )

        self.default = default

        # Be careful here, the problem is each
        # time the field is used, a validator
        # is added for each new value added which
        # creates an array containing the same
        # validator
        if self.max_length is not None:
            # self._validators.append(MaxLengthValidator(self.max_length))
            self._validators.add(model_validators.MaxLengthValidator(self.max_length))

        if not self.null:
            # self._validators.append(validators.validate_is_not_null)
            self._validators.add(model_validators.validate_is_not_null)

    def _true_value_or_default(self, value):
        if self.default is not None and value is None:
            return self.default
        return value

    def _run_validation(self, value):
        # Default values should be validated
        # too ? Otherwise the use might enter
        # anykind of none validated value ??

        validators_result = None
        for validator in self._validators:
            if not callable(validator):
                raise TypeError('Validator should be a callable')
            if validators_result is None:
                validators_result = validator(value)
            else:
                validators_result = validator(validators_result)
        return validators_result or value

    def _check_or_convert_to_type(self, value, object_to_check_against,
                                  message, enforce=True, force_conversion=False,
                                  use_default=False):
        """
        Checks the validity of a value against a Python object for example
        an int, a str or a list

        This check is used only to make sure that a value corresponds
        specifically to a python object with the possibility of raising
        an error if not or force converting the value to the python
        object in question

        Parameters
        ----------

                value (str, int, type): value to test
                object_to_check_against (type): int, str, type
                message (str): message to display
                enforce (bool, optional): whether to raise an error. Defaults to True
                force_conversion (bool, optional): try to convert the value to obj. Defaults to False

        Raises
        ------

                TypeError: the value is not of the same type of the python object

        Returns
        -------

                Any: int, str
        """
        if force_conversion:
            try:
                value = object_to_check_against(value)
            except:
                # Thing is the validators know how to use
                # the default value which is not the case
                # when calling this specific function
                if use_default:
                    return self.default

        result = isinstance(value, object_to_check_against)
        if not result:
            if enforce:
                raise TypeError(message)

        return value

    def resolve(self, value: Any):
        """
        Resolves a given value by cleaning it and calling
        a series of default validators and checks before
        returning the normalized item

        Subclasses should implement their own resolve function
        with it's own custom logic because this resolve definition
        is more to implement some standardized resolution more than
        anything else

        Parameters
        ----------

                value (str, int, float): a valid python object

        Returns
        -------

                str, int, float: a valid python object
        """
        true_value = None
        if isinstance(value, beautiful_soup_tag):
            true_value = value.text

        # There might be a case where a None
        # value slides in and breaks the
        # rest of the process -;
        # deal with that here
        if value is None:
            if self.default is not None:
                return self.default
            return value
        
        # To simplify the whole process,
        # make sure we are dealing with 
        # a string even though it's an
        # integer, float etc.
        # true_value = self._true_value_or_default(str(value))
        true_value = str(value)

        # Ensure the value to work with
        # is as clean as possible
        if '>' in true_value or '<' in true_value:
            true_value = html.remove_tags(value)

        clean_value = deep_clean(true_value)

        # Here, try to convert the value to it's
        # true self (instead of returning) string but
        # the problem is when a subclass that has a _dtype
        # of int invoks this superclass e.g. AgeField
        # through another subclass e.g. AgeField(DateField),
        # this creates an error because the value
        # that is passed (a data string) is obviously
        # not an integer. This then creates and error.
        if clean_value.isnumeric():
            if self._dtype == numpy.int:
                clean_value = int(clean_value)

            if self._dtype == numpy.float:
                clean_value = float(clean_value)
            
        true_value = self._run_validation(clean_value)
        # self._cached_result = true_value
        self._cached_result = self._true_value_or_default(true_value)
        return self._cached_result


class CharField(Field):
    """
    Field for text

    Args:
        max_length (int, optional): [description]. Defaults to None.
        null (bool, optional): [description]. Defaults to True.
        default (Any, optional): [description]. Defaults to None.
        validators (Union[List[Callable[[Any], Any], Tuple[Callable[[Any], Any]]]], optional): [description]. Defaults to [].
    """
    name = 'char'

    def resolve(self, value):
        result = self._check_or_convert_to_type(
            value,
            str,
            'Value should be a string',
            force_conversion=True
        )
        self._cached_result = super().resolve(result)


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

    def __init__(self, limit_to_domains: Union[List[str], Tuple[str]] = [], **kwargs):
        null = kwargs.get('null')
        default = kwargs.get('default')
        validators = kwargs.get('validators', [])
        super().__init__(null=null, default=default, validators=validators)
        self.limit_to_domains = limit_to_domains

    def _check_domain(self, domain):
        if self.limit_to_domains:
            if domain not in self.limit_to_domains:
                self._cached_result = self.default

    def resolve(self, value):
        value = super().resolve(value)
        if value is not None:
            _, domain = value.split('@')
            self._check_domain(domain)


class UrlField(Field):
    name = 'url'
    _default_validators = [model_validators.validate_url]

    def resolve(self, url):
        # TODO: This can be simplified into a single
        # unified check ????
        result = self._check_or_convert_to_type(
            url, str, 'Link should be of type string', force_conversion=True
        )
        url = super().resolve(result)
        self._cached_result = safe_download_url(canonicalize_url(url))


class ImageField(UrlField):
    """
    Field for representing an image url in a model

    Parameters
    ----------

            download (bool, optional): download the image. Defaults to False
            as_thumbnail (bool, optional): download as a thumnail. Defaults to False
            download_to (str, optional): download image to a specific path. Defaults to None
    """
    field_name = 'image'

    def __init__(self, download=False, as_thumnail=False, download_to: str=None):
        super().__init__()
        self.download = download
        self.as_thumbnail = as_thumnail
        self.image_data = None
        self.metadata = {}
        self.download_to = download_to

    def resolve(self, url):
        super().resolve(url)

        if self.download:
            download_image_from_url(
                url,
                download_to=self.download_to,
                as_thumbnail=self.as_thumbnail
            )


class IntegerField(Field):
    """
    Field for numbers

    Args:
        default (Any, optional): [description]. Defaults to None.
        min_value (int, optional): [description]. Defaults to None.
        max_value (int, optional): [description]. Defaults to None.
    """
    name = 'integer'
    _dtype = numpy.int

    def __init__(self, default: Any = None, min_value: int = None, max_value: int = None):
        super().__init__(default=default)
        if min_value is not None:
            self._validators.add(model_validators.MinLengthValidator(min_value))

        if max_value is not None:
            self._validators.add(model_validators.MaxLengthValidator(max_value))

    def resolve(self, value):
        self._cached_result = super().resolve(value)
        self._cached_result = self._check_or_convert_to_type(
            self._cached_result,
            int,
            'Value should be an integer',
            force_conversion=True,
            use_default=True
        )


class DecimalField(Field):
    name = 'float'
    _dtype = numpy.float

    def __init__(self, default: Any = None, 
                 min_value: int = None, max_value: int = None):
        if min_value is not None:
            self._validators.add(model_validators.MinLengthValidator)

        if max_value is not None:
            self._validators.add(model_validators.MaxLengthValidator)

        super().__init__(default=default)

    def resolve(self, value):
        result = super().resolve(value)
        self._cached_result = self._check_or_convert_to_type(
            result, float, 'Value should be a float/decimial', force_conversion=True
        )


class DateField(Field):
    name = 'date'

    def __init__(self, date_format: str, default: Any = None, tz_info = None):
        super().__init__(default=default)
        self.date_format = date_format
        if tz_info is None:
            tz_info = pytz.UTC
        self.tz_info = tz_info

    def __str__(self):
        return str(self._cached_result.date())
    
    def resolve(self, date):
        result = super().resolve(date)
        self._cached_result = datetime.datetime.strptime(
            date, self.date_format
        )


class AgeField(DateField):
    name = 'age'
    _dtype = numpy.int

    def __str__(self):
        return str(self._cached_result)

    def _substract(self) -> int:
        current_date = datetime.datetime.now()
        return current_date.year - self._cached_result.year

    def resolve(self, date):
        super().resolve(date)
        self._cached_result = self._substract()


class FunctionField(Field):
    """
    The Function field takes a field and passes
    its result to a set of different custom definitions
    before returning the final value

    Example
    -------

            def addition(value):
                return value + 1

            class MyModel(Model):
                age = Function(NumberField(), addition)

    Args:
        output_field (Field, optional): [description]. Defaults to None.
        default (Any, optional): [description]. Defaults to None.
        validators (Validators, optional): [description]. Defaults to [].

    Raises:
        TypeError: [description]
        TypeError: [description]
    """
    name = 'function'
    _dtype = numpy.object

    def __init__(self, *methods: Callable[[Any], Any], output_field: Field = None, 
                 default: Any = None, validators = []):
        super().__init__(default=default, validators=validators)
        self.filtered_methods = []
        self.output_field = output_field

        if output_field is not None:
            if not isinstance(output_field, Field):
                raise TypeError(("The output field should be one of "
                        "zineb.models.fields types e.g. CharField and should be "
                        "instanciated e.g. FunctionField(output_field=CharField())"))
        else:
            self.output_field = CharField()
        
        incorrect_elements = []
        for method in methods:
            if not callable(method):
                incorrect_elements.append(method)
            self.filtered_methods.append(method)

        if incorrect_elements:
            raise TypeError((f"You should provide a list of a callables. "
                f"Instead got: {incorrect_elements}"))

    def resolve(self, value):
        self._cached_result = super().resolve(value)

        new_cached_result = None
        if self.filtered_methods:
            for method in self.filtered_methods:
                if new_cached_result is None:
                    new_cached_result = method(self._cached_result)
                else:
                    new_cached_result = method(new_cached_result)
            self._cached_result = new_cached_result
            self.output_field.resolve(self._cached_result)
            self._cached_result = self.output_field._cached_result


class ObjectFieldMixins:
    @staticmethod
    def _detect_object_in_string(value):
        return ast.literal_eval(value)


class ArrayField(ObjectFieldMixins, Field):
    name = 'list'
    _dytpe = numpy.object

    def __init__(self, output_field: Field, default: Any = None, validators = []):
        super().__init__(default=default, validators=validators)
        self.output_field = output_field
        
        if output_field is not None and not isinstance(output_field, Field):
            raise TypeError("The output field should be one of zineb.models.fields. Did you forget to instantiate the field?")

    def resolve(self, value) -> numpy.array:
        if isinstance(value, str):
            value = self._detect_object_in_string(value)

        result = self._check_or_convert_to_type(
            value, list, 'Value should be of type list'
        )

        def get_output_resolution(value):
            self.output_field.resolve(value)
            return self.output_field._cached_result
        resolved_values = map(get_output_resolution, result)

        self._cached_result = numpy.array(list(resolved_values))
        return self._cached_result


class JsonField(ObjectFieldMixins, Field):
    def resolve(self, value):
        if isinstance(value, str):
            value = self._detect_object_in_string(value)
        self._cached_result = super().resolve(value)


class CommaSeperatedField(Field):
    name = 'comma_separated'
    _dtype = numpy.str

    def __init__(self, max_length: int = None):
        super().__init__(max_length=max_length)

    def resolve(self, values: Union[List[Any], Tuple[Any]]):
        self._check_or_convert_to_type(
            values, list, 'Values should of type list', force_conversion=True
        )

        output_values_as = CharField()
        resolved_values = []
        for value in values:
            output_values_as.resolve(value)
            resolved_values.append(output_values_as._cached_result)

        self._cached_result = ','.join(resolved_values)


class RegexField(Field):
    name = 'regex'

    def __init__(self, pattern: str, group: int = 0, output_field: Field=None, **kwargs):
        self.pattern = re.compile(pattern)
        self.group = group
        self.output_field = output_field
        super().__init__(**kwargs)

    def resolve(self, value):
        regexed_value = self.pattern.search(value)
        if regexed_value:
            true_value = regexed_value.group(self.group)
            if self.output_field is not None:
                if isinstance(self.output_field, Field):
                    self._cached_result = self.output_field.resolve(true_value)
                else:
                    raise TypeError((f"Output field should be a instance of " 
                    "zineb.fields.Field. Got: {self.output_field}"))
            else:
                self._cached_result = super().resolve(true_value)


# class RelatedField(Field):
#     name = 'related'
#     _dtype = numpy.object
#     relation = None

#     def __init__(self, to, default=None, validators: List=[]):
#         self.to_field = to
#         self.to_field_object = None
#         super().__init__(default=default, validators=validators)

#     def __getattr__(self, name):
#         if name == 'relation':
#             if self.relation is None:
#                 raise ValueError(f"{self.relation} should be an actual relationship to a Model field")

#     def __setattr__(self, name, value):
#         if name == 'relation':
#             if not callable(value) or not isinstance(value, Field):
#                 raise ValueError(f"{self.relation} should be an actual relationship to a Model field")

#     def resolve(self):
#         self._cached_result = self.relation._cached_result


# class Value:
#     result = None

#     def __init__(self, result, field_name=None):
#         self.result = result
#         self.field_name = field_name

#     def __str__(self):
#         return self.result

#     def __repr__(self):
#         return f"{self.__class__.__name__}({self.result})"

#     def __add__(self, value):
#         if isinstance(self.result, tuple):
#             self.result = list(self.result)

#         if isinstance(self.result, list):
#             self.result.extend([value])
#             return self.result
#         return self.result + value

#     def __setattr__(self, name, value):
#         if name == 'result':
#             value = deep_clean(value)
#         return super().__setattr__(name, value)
