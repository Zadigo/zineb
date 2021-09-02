import ast
import datetime
import json
import re
from typing import Any, Callable, Iterable, List, Tuple, Union

import numpy
import pandas
import pytz
from bs4.element import Tag as beautiful_soup_tag
from w3lib import html
from w3lib.url import canonicalize_url, safe_download_url
from zineb.models import validators as model_validators
from zineb.utils._html import deep_clean
from zineb.utils.images import download_image_from_url


class Field:
    """
    This is the base class for all field classes
    """

    name = None
    _cached_result = None
    _default_validators = []
    _dtype = numpy.str

    def __init__(self, max_length: int=None, null: bool=True, 
                 default: Union[str, int, float]=None, validators=[]):
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
        # is added for each new value added which
        # creates an array containing the same
        # validator
        if self.max_length is not None:
            self._validators.add(model_validators.MaxLengthValidator(self.max_length))

        if not self.null:
            self._validators.add(model_validators.validate_is_not_null)

    def _true_value_or_default(self, value):
        if self.default is not None and value is None:
            return self.default
        return value

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

            if validator_return_value is None:
                validator_return_value = validator(value)
            else:
                validator_return_value = validator(validator_return_value)
        return validator_return_value or value

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

            - value (str, int, type): value to test
            - object_to_check_against (type): int, str, type
            - message (str): message to display
            - enforce (bool, optional): whether to raise an error. Defaults to True
            - force_conversion (bool, optional): try to convert the value to obj. Defaults to False

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

    def _convert_to_type(self, value, t=None):
        try:
            return t(value) if t is not None else self._dtype(value)
        except Exception:
            raise ValueError((f"The value {value} does not match"
            f" the type provided in {self._dtype}. Got {type(value)}"
            f"instead of {self._dtype}"))

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
        # deal with that here by running
        # validations directly and returning
        # either a default value or the value
        if value is None:
            # return self._true_value_or_default(value)
            self._cached_result = self._run_validation(value)
            return self._cached_result
        
        # To simplify the whole process,
        # make sure we are dealing with 
        # a string even though it's an
        # integer, float etc.
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
            
        self._cached_result = self._run_validation(clean_value)
        return self._cached_result


class CharField(Field):
    """
    Field for text

    Parameters
    ----------
    
        - max_length (int, optional): [description]. Defaults to None.
        - null (bool, optional): [description]. Defaults to True.
        - default (Any, optional): [description]. Defaults to None.
        - validators (): [description]. Defaults to [].
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
        # result = self._check_or_convert_to_type(
        #     url, str, 'Link should be of type string', force_conversion=True
        # )
        url = super().resolve(url)
        if url is not None:
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
    name = 'image'

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

    Parameters
    ----------

        - default (Any, optional): Default value if None. Defaults to None.
        - min_value (int, optional): Minimum value. Defaults to None.
        - max_value (int, optional): Maximum value. Defaults to None.
    """
    name = 'integer'
    _dtype = numpy.int

    def __init__(self, default: Any=None, min_value: int=None, max_value: int=None):
        super().__init__(default=default)

        if min_value is not None:
            self._validators.add(model_validators.MinLengthValidator(min_value))

        if max_value is not None:
            self._validators.add(model_validators.MaxLengthValidator(max_value))

    def resolve(self, value):
        result = super().resolve(value)
        self._cached_result = self._convert_to_type(result)


class DecimalField(Field):
    name = 'float'
    _dtype = float

    def __init__(self, default: Any=None, 
                 min_value: int=None, max_value: int=None):
        if min_value is not None:
            self._validators.add(model_validators.MinLengthValidator)

        if max_value is not None:
            self._validators.add(model_validators.MaxLengthValidator)

        super().__init__(default=default)

    def resolve(self, value):
        result = super().resolve(value)
        self._cached_result = self._convert_to_type(result)


class DateField(Field):
    name = 'date'

    def __init__(self, date_format: str, 
                 default: Any=None, tz_info=None):
        super().__init__(default=default)
        self.date_format = date_format
        if tz_info is None:
            tz_info = pytz.UTC
        self.tz_info = tz_info
    
    def resolve(self, date: str):
        result = super().resolve(date)
        self._cached_result = datetime.datetime.strptime(
            result, self.date_format
        )


class AgeField(DateField):
    name = 'age'
    _dtype = numpy.int

    def __init__(self, date_format: str,
                 default: Any = None, tz_info=None):
        super().__init__(date_format=date_format, 
                         default=default, tz_info=tz_info)
        self._cached_date = None

    def _substract(self) -> int:
        current_date = datetime.datetime.now()
        return current_date.year - self._cached_result.year

    def resolve(self, date):
        super().resolve(date)
        self._cached_date = self._cached_result
        self._cached_result = self._convert_to_type(self._substract())


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
    _dytpe = numpy.array

    def __init__(self, default: Any = None, 
                 validators = []):
        super().__init__(default=default, validators=validators)

    def resolve(self, value):
        if isinstance(value, str):
            value = self._detect_object_in_string(value)

        result = self._convert_to_type(value, t=list)

        self._cached_result = pandas.Series(result)
        return self._cached_result


class JsonField(ObjectFieldMixins, Field):
    def __init__(self, validators=[]):
        super().__init__(validators=validators)

    def resolve(self, value):
        result = super().resolve(value)
        if isinstance(result, str):
            result = self._detect_object_in_string(result)

        if not isinstance(result, dict):
            raise ValueError(f"JsonField should receive a dict as value.")

        self._cached_result = json.dumps(result)


class CommaSeperatedField(Field):
    name = 'comma_separated'

    def __init__(self, max_length: int = None):
        super().__init__(max_length=max_length)

    def resolve(self, values: Union[List[Any]]):
        values = self._convert_to_type(values, t=list)
        resolved_values = map(lambda x: str(x), values)
        self._cached_result = ','.join(resolved_values)


class RegexField(Field):
    name = 'regex'

    def __init__(self, pattern: str, group: int = 0, output_field: Field=None, **kwargs):
        self.pattern = re.compile(pattern)
        self.group = group
        self.output_field = output_field
        super().__init__(**kwargs)

    def resolve(self, value: str):
        regexed_value = self.pattern.search(value)
        if regexed_value:
            result = regexed_value.group(self.group)

            if self.output_field is not None:
                if not isinstance(self.output_field, Field):
                    raise TypeError((f"Output field should be a instance of " 
                    "zineb.fields.Field. Got: {self.output_field}"))
                self._cached_result = self.output_field.resolve(result)
            else:
                self._cached_result = super().resolve(result)


class Value:
    """
    The simplest Python representation of a value

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

    def __add__(self, value):
        if isinstance(self.result, tuple):
            self.result = list(self.value)

        if isinstance(self.result, list):
            self.result.extend([value])
            return self.result
        return self.result + str(value)

    def __setattr__(self, name, value):
        if name == 'result':
            value = deep_clean(value)
        return super().__setattr__(name, value)
