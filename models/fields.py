import ast
import datetime
import json
from typing import Type

import numpy
import pandas
import pytz
from bs4.element import Tag as beautiful_soup_tag
from w3lib import html
from w3lib.url import canonicalize_url, safe_download_url
from zineb.http.request import HTTPRequest
from zineb.models import validators
from zineb.models.validators import MaxLengthValidator, MinLengthValidator
from zineb.utils._html import deep_clean
from zineb.utils.general import download_image


class Field:
    """ 
    This is the base class for all field classes

    Parameters
    ----------
    
            TypeError: [description]
            ValidationError: [description]
    """

    name = None
    _cached_result = None
    _default_validators = []
    _dtype = numpy.str

    def __init__(self, max_length=None, null=True, 
                 default=None, validators:list = []):
        self.max_length = max_length
        self.null = null
        self._validators = validators

        if self._default_validators:
            self._validators = self._validators + self._default_validators

        self.default = default

    def _true_value_or_default(self, value):
        return str(value) if value is not None else str(self.default)

    def _run_validation(self, value):
        # Default values should be validated
        # too ? Otherwise the use might enter
        # anykind of none validated value ??


        if self.max_length:
            self._validators.append(MaxLengthValidator(self.max_length))

        if self.null:
            self._validators.append(validators.validate_is_not_null)

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
                                  message, enforce=True, force_conversion=False):
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
            value = object_to_check_against(value)

        result = isinstance(value, object_to_check_against)
        if not result:
            if enforce:
                raise TypeError(message)

        return value

    def resolve(self, value):
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
        self._cached_result = true_value
        return true_value


class CharField(Field):
    name = 'char'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

    def __init__(self, max_length=500, **kwargs):
        super().__init__(max_length=max_length, **kwargs)


class NameField(CharField):
    name = 'name'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def resolve(self, value):
        super().resolve(value)
        self._cached_result = self._cached_result.lower().title()


class EmailField(Field):
    _default_validators = [validators.validate_email]

    def __init__(self, limit_to_domains: list = [], **kwargs):
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
        _, domain = value.split('@')
        self._check_domain(domain)


class UrlField(Field):
    name = 'url'
    _default_validators = [validators.validate_url]

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

    def __init__(self, download=False, as_thumnail=False, download_to=None):
        super().__init__()
        self.download = download
        self.as_thumbnail = as_thumnail
        self.image_data = None
        self.metadata = {}
        self.download_to = download_to

    def resolve(self, url):

        super().resolve(url)

        if self.download:
            request = HTTPRequest(self._cached_result, is_download_url=True)
            request._send()
            self.image_data = download_image(
                request._http_response, 
                download_to=self.download_to, 
                as_thumbnail=self.as_thumbnail
            )


class IntegerField(Field):
    name = 'integer'
    _dtype = numpy.int

    def __init__(self, default=None, min_value=None, max_value=None):
        super().__init__(default=default)
        if min_value is not None:
            self._validators.append(MinLengthValidator(min_value))

        if max_value is not None:
            self._validators.append(MaxLengthValidator(max_value))

    def resolve(self, value):
        self._cached_result = super().resolve(value)
        self._cached_result = self._check_or_convert_to_type(
            self._cached_result, int, 'Value should be an integer', force_conversion=True
        )


class DecimalField(Field):
    name = 'float'
    _dtype = numpy.float

    def __init__(self, default=None, min_value=None, max_value=None):
        if min_value is not None:
            pass

        if max_value is not None:
            pass

        super().__init__(default=default)

    def resolve(self, value):
        result = super().resolve(value)
        self._cached_result = self._check_or_convert_to_type(
            result, float, 'Value should be a float/decimial', force_conversion=True
        )


class DateField(Field):
    name = 'date'

    def __init__(self, date_format, default=None, tz_info=None):
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

    def _substract(self):
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
    """
    name = 'function'
    _dtype = numpy.object

    def __init__(self, *methods, output_field=None, default=None, validators=[]):
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

    def __init__(self, output_field, default=None, validators=[]):
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

    def __init__(self, max_length=None):
        super().__init__(max_length=max_length)

    def resolve(self, values):
        self._check_or_convert_to_type(
            values, list, 'Values should of type list', force_conversion=True
        )

        output_values_as = CharField()
        resolved_values = []
        for value in values:
            output_values_as.resolve(value)
            resolved_values.append(output_values_as._cached_result)

        self._cached_result = ','.join(resolved_values)


class Value:
    def __init__(self, result, field_name=None):
        self.result = result
        self.field_name = field_name

    def __str__(self):
        return self.result

    def __repr__(self):
        return f"{self.__class__.__name__}({self.result})"
