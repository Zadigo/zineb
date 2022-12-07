import datetime
import re
from typing import Any, List

from bs4.element import Tag as beautiful_soup_tag
from w3lib import html
from w3lib.url import canonicalize_url, safe_download_url

from zineb.checks import messages
from zineb.exceptions import ValidationError
from zineb.models import validators as model_validators
from zineb.settings import settings
from zineb.utils.characters import deep_clean
from zineb.utils.conversion import detect_object_in_string
from zineb.utils.encoders import DefaultJsonEncoder
from zineb.utils.formatting import LazyFormat
from zineb.utils.images import download_image_from_url


class Empty:
    """
    Class that represents '' as a Python object.
    These string are not considered None in Python
    but do no have any value
    """

    def __repr__(self):
        return 'Empty'

    def __str__(self):
        return ''

    def __contains__(self, value):
        """A bland definition used to prevent an error
        when x in ... is called on the class"""
        return False

    def __eq__(self, value):
        return (
            value == '' or
            value == 'Empty'
        )


class Value:
    """
    Interface that represents the raw value 
    that comes from the internet. It is stripped 
    from whitespace and the html tags are removed

    >>> Value("some data")
    ... "some data"
    """
    result = None

    def __init__(self, value, output_field=None):
        self.result = value
        self.field_name = None
        self.output_field = output_field

    def __str__(self):
        # Treat all values that are returned
        # as a string even though the pure
        # representation is an int, float...
        return str(self.result)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.result})"

    def __eq__(self, value):
        return value == self.result

    def __hash__(self):
        return hash((self.result, self.field_name))

    def __setattr__(self, name, value):
        if name == 'result':
            if value is None:
                return super().__setattr__(name, value)

            if isinstance(value, Value):
                value = str(value)

            if isinstance(value, beautiful_soup_tag):
                try:
                    value = value.text
                except:
                    message = LazyFormat(
                        "Could not get attribute text from '{value}'.", value=value)
                    raise AttributeError(message)

            if not isinstance(value, (str, int, float, list, dict)):
                message = LazyFormat('{value} should be a string, '
                                     'an integer, a list, a dict or a float.', value=value)
                raise ValueError(message)

            # NOTE: Technically all the values that come
            # from the internet a strings. However the user
            # might want to pass his value which is not
            # necessarily a string and we need to be
            # able to accept it without throwing and error
            if isinstance(value, str):
                value = deep_clean(value)

                if '>' in value or '<' in value:
                    value = html.remove_tags(value)

            # TODO:
            # if self.output_field is not None:
            #     value = self.output_field._simple_resolve(value)

        return super().__setattr__(name, value)

    @property
    def is_empty(self):
        return (
            self.result == None or
            self.result == ''
        )

    @property
    def is_value_instance(self):
        return True


class DeferredAttribute:
    """A base class for deferred-loading of the data
    corresponding to a field on the data container 
    of a model field

    >>> class MyModel(Model):
            name = fields.CharField()  
    ... model.name
    ... [..., ...]
    """

    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        data = instance.__dict__
        field_name = self.field.field_name
        if field_name not in data:
            field_data = instance._data_container.get_container(field_name)
            data[field_name] = field_data
        return data[field_name]


class OneToOneDescriptor(DeferredAttribute):
    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        data = instance.__dict__
        field_name = self.field.field_name
        if field_name not in data:
            data[field_name] = self.field.related_model
        return data[field_name]


class Field:
    """Base class for all fields """

    field_descriptor = DeferredAttribute
    _cached_result = None
    _default_validators = []
    _validation_error_message = ("The value '{value}' does not match the type provided "
                                 "in {t}. Got {type1} instead of {type2} for model field '{name}'.")

    def __init__(self, max_length=None, null=True, default=None, validators=[]):
        self.model = None
        # Use '' instead of None to be able to
        # test checks when using test comparision
        # on field_name
        self.field_name = ''

        self.max_length = max_length
        self.null = null

        self._validators = set(validators)
        if self._default_validators:
            self._validators = (
                self._validators |
                set(self._default_validators)
            )

        self.default = default
        self.creation_counter = 0

        # FIXME: Be careful here, the problem is each
        # time the field is used, a validator
        # is added for each new value which
        # creates an array containing the same
        # validators
        if self.max_length is not None:
            self._validators.add(
                model_validators.MaxLengthValidator(self.max_length))

        if not self.null:
            self._validators.add(model_validators.validate_is_not_null)

        # self._meta_attributes = {}

    def __hash__(self):
        return hash((self.model._meta.verbose_name, self.field_name))

    # def _bind(self, field_name, model=None):
    #     """Bind the field's name registered
    #     on the model to this instance and the
    #     model instance itself"""
    #     self._meta_attributes.update(field_name=field_name)
    #     current_model = self._meta_attributes.get('model', None)

    #     if current_model is None and model is not None:
    #         self._meta_attributes['model'] = model

    @property
    def internal_type(self):
        """Determines the internal 
        python type of the field"""
        return str

    @property
    def internal_name(self):
        return None

    def _true_value_or_default(self, value):
        # ENHANCE: Check against Empty is not a valid or useful
        # type check anymore since we can check emptyness
        # directly on the Value instance
        if value is None and self.default is not None:
            return self.default
        elif value == 'Empty' and self.default is not None:
            return self.default
        else:
            return value

    def _to_python_object(self, value):
        """
        A helper function that returns the true 
        python representation of a given value

        NOTE: Subclasses should implement their own
        way of returning said representation
        """
        return value

    def _run_validation(self, value):
        # Default values should be validated
        # too in order to keep consistency in
        # the model
        value = self._true_value_or_default(value)

        if value is None:
            return None

        # validator_return_value = None
        for validator in self._validators:
            if not callable(validator):
                raise TypeError('A Validator should be a callable.')
            try:
                # if validator_return_value is None:
                #     validator_return_value = validator(value)
                # else:
                #     validator_return_value = validator(validator_return_value)
                # NOTE: Validators should not return any value
                # instead, they should just validate that a
                # value respects a certan logic and if not raise
                # a ValidationError
                validator(value)
            except:
                message = ("A validation error occured on "
                           "field '{name}' with value '{value}'.")
                raise Exception(LazyFormat(
                    message,
                    name=self.field_name,
                    value=value
                )
                )
        # if self._validators:
        #     return validator_return_value
        return value

    # TODO: Rename this method
    def _check_emptiness(self, value):
        """
        Deals with true empty values e.g. '' that
        are factually None but get passed
        around as containing data

        The Empty class is the pythonic representation
        for these kinds of strings
        """
        if value == '':
            return Empty()
        return value

    def _simple_resolve(self, clean_value):
        """
        A value resolution method that only runs validations.

        This definition is useful for example for revalidating the end
        result value of a field that does not require any cleaning
        or normalization.

        NOTE: This should ONLY be used internally and
        not on incoming data from the web since it does
        not apply any kind of formatting (spaces, escape
        characters or HTML tags) but only validations
        """
        if getattr(clean_value, 'is_empty', False):
            result = clean_value or None
        else:
            result = self._to_python_object(clean_value)
        self._cached_result = self._run_validation(result)

    def checks(self):
        """Run global checks on the Field. Other specific
        fields need to implement their other other additional
        checking method"""
        def check_field_name():
            if self.field_name.endswith('__'):
                return [
                    messages.ErrorMessage(
                        f"{self.field_name} is not a valid field name",
                        obj=self
                    )
                ]

            if '__' in self.field_name:
                return [
                    messages.ErrorMessage(
                        f"{self.field_name} cannot have '__' in the name",
                        obj=self
                    )
                ]

            if self.field_name == 'pk' or self.field_name == 'id':
                return [
                    messages.ErrorMessage(
                        f"{self.field_name} cannot be 'id' or 'pk' which are reserved keywords",
                        obj=self
                    ),
                ]
            return []

        def check_validators():
            errors = []
            for validator in self._validators:
                if not callable(validator):
                    errors.append(
                        messages.ErrorMessage(
                            f'Validators have be a callable',
                            obj=validator
                        )
                    )
            return errors

        def check_null():
            if not isinstance(self.null, bool):
                return [
                    messages.ErrorMessage(
                        f"null attribute should be a boolean",
                        obj=self
                    )
                ]
            return []

        return [
            *check_field_name(),
            *check_validators(),
            *check_null()
        ]

    def update_model_options(self, model, field_name):
        self.model = model
        self.field_name = field_name
        model._meta.add_field(self.field_name, self)
        # Since we removed the original declared field
        # on the model, we replace it with a descriptor
        # that will allow the user to directly load the
        # field's data from the data container directly
        # as opposed to returning the Field class
        setattr(model, self.field_name, self.field_descriptor(self))

    def resolve(self, value):
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
        self._simple_resolve(value)


class CharField(Field):
    @property
    def internal_name(self):
        return 'CharField'

    def _to_python_object(self, value):
        if value is None:
            return value

        return self.internal_type(value)

    def checks(self):
        errors = super().checks()

        def check_max_length():
            if self.max_length is not None:
                if (not isinstance(self.max_length, int) or self.max_length < 0):
                    return [
                        messages.ErrorMessage(
                            "'max_length' attribute should be a positive integer",
                            obj=self
                        )
                    ]
            return []

        errors.extend([
            *check_max_length()
        ])
        return errors


class TextField(CharField):
    def __init__(self, max_length = 500, **kwargs):
        super().__init__(max_length=max_length, **kwargs)

    @property
    def internal_name(self):
        return 'TextField'


class NameField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def internal_name(self):
        return 'NameField'

    def _to_python_object(self, value):
        result = super()._to_python_object(value)
        if result is None:
            return result
        return result.lower().title()


class EmailField(CharField):
    _default_validators = [model_validators.validate_email]

    def __init__(self, limit_to_domains=[], null=False, default=None, validators=[]):
        super().__init__(null=null, default=default, validators=validators)
        self.limit_to_domains = limit_to_domains

    @property
    def internal_name(self):
        return 'EmailField'

    def _check_domain(self, domain):
        if self.limit_to_domains:
            if domain not in self.limit_to_domains:
                raise ValidationError(f'{domain} is not in valid domains.')

    def resolve(self, value):
        super().resolve(value)
        if self._cached_result is not None or self._cached_result != 'Empty':
            _, domain = str(value).split('@')
            self._check_domain(domain)


class URLField(CharField):
    _default_validators = [model_validators.validate_url]

    @property
    def internal_name(self):
        return 'URLField'

    def resolve(self, url):
        super().resolve(url)
        if self._cached_result is not None:
            url = canonicalize_url(self._cached_result)
            self._cached_result = safe_download_url(url)
            # result = safe_download_url(canonicalize_url(url))


class ImageField(URLField):
    def __init__(self, max_length=None, null=True, validators=[],
                 download=False, as_thumnail=False, download_to=None):
        valid_extensions = ['jpeg', 'jpg', 'png']
        self._default_validators.extend(
            [model_validators.validate_extension(valid_extensions)])

        super().__init__(max_length=max_length, null=null, validators=validators)

        self.download = download
        self.as_thumbnail = as_thumnail
        # self.image_data = None
        # self.metadata = {}
        self.download_to = download_to

    @property
    def internal_name(self):
        return 'ImageField'

    def resolve(self, url):
        super().resolve(url)

        if self.download:
            download_image_from_url(
                self._cached_result,
                download_to=self.download_to,
                as_thumbnail=self.as_thumbnail
            )


class IntegerField(Field):
    def __init__(self, default=None, min_value=None, max_value=None, validators=[]):
        super().__init__(default=default, validators=validators)
        self.min_value = min_value
        self.max_value = max_value

        if min_value is not None:
            self._validators.add(
                model_validators.MinLengthValidator(min_value))

        if max_value is not None:
            self._validators.add(
                model_validators.MaxLengthValidator(max_value))

    @property
    def internal_type(self):
        return int

    @property
    def internal_name(self):
        return 'IntegerField'

    def _to_python_object(self, value):
        try:
            return self.internal_type(str(value))
        except:
            if not isinstance(value, (int, float)):
                attrs = {
                    'value': value,
                    't': self.__class__.__name__,
                    'type1': type(value),
                    'type2': self.internal_type,
                    'name': self.field_name
                }
                raise ValidationError(LazyFormat(
                    self._validation_error_message, **attrs))

    def checks(self):
        errors = super().checks()

        def check_min_and_max_values():
            if self.min_value is not None:
                if not isinstance(self.min_value, int) and self.min_value < 0:
                    return [
                        messages.ErrorMessage(
                            f"min_value attribute should be a positive integer")
                    ]

            if self.max_value is not None:
                if not isinstance(self.max_value, int) and self.max_value < 0:
                    return [
                        messages.ErrorMessage(
                            f"max_value attribute should be a positive integer")
                    ]
            return []

        errors.extend([
            *check_min_and_max_values()
        ])
        return errors


class DecimalField(IntegerField):
    @property
    def internal_type(self):
        return float

    @property
    def internal_name(self):
        return 'DecimalField'


class DateFieldsMixin:
    def __init__(self, date_format=None, default=None):
        super().__init__(default=default)

        self.date_parser = datetime.datetime.strptime
        self._datetime_object = None

        formats = set(getattr(settings, 'DEFAULT_DATE_FORMATS'))
        formats.add(date_format)
        self.date_formats = formats
        self.date_format = date_format

    def _to_python_object(self, result):
        for date_format in self.date_formats:
            try:
                d = self.date_parser(str(result), date_format)
            except:
                d = None
            else:
                if d:
                    break

        if d is None:
            message = LazyFormat("Could not find a valid format for "
                                 "date '{d}' on field '{name}'.", d=result, name=self.field_name)
            raise ValidationError(message)
        self._datetime_object = d
        return d.date()

    def checks(self):
        errors = super().checks()
        if not isinstance(self.date_format, str):
            errors.extend([
                messages.ErrorMessage(
                    f"'date_format' attribute should be a string",
                    obj=self
                )
            ])
        return errors


class DateField(DateFieldsMixin, Field):
    @property
    def internal_type(self):
        return datetime.datetime

    @property
    def internal_name(self):
        return 'DateField'

    # def _function_resolve(self, func):
    #     super()._function_resolve(func)
    #     self._cached_result = self._datetime_object.date()


class AgeField(DateFieldsMixin, Field):
    def __init__(self, date_format=None, default=None):
        super().__init__(date_format=date_format, default=default)

    @property
    def internal_type(self):
        return int

    @property
    def internal_name(self):
        return 'AgeField'

    def _substract(self):
        current_date = datetime.datetime.now()
        return current_date.year - self._datetime_object.year

    def resolve(self, date: str):
        super().resolve(date)
        self._cached_result = self._substract()


class MappingFieldMixin:
    def _to_python_object(self, value):
        result = detect_object_in_string(str(value))
        if not isinstance(result, (list, dict)):
            attrs = {
                'value': value,
                't': self.__class__.__name__,
                'type1': type(value),
                'type2': self.internal_type,
                'name': self.field_name
            }
            raise ValidationError(LazyFormat(
                self._validation_error_message, **attrs))
        return result


class ListField(MappingFieldMixin, Field):
    def __init__(self, default=None, validators=[]):
        super().__init__(default=default, validators=validators)

    @property
    def internal_type(self):
        return list

    @property
    def internal_name(self):
        return 'ListField'


class JsonField(MappingFieldMixin, Field):
    def __init__(self, default=None, validators=[]):
        super().__init__(default=default, validators=validators)

    @property
    def internal_type(self):
        return dict

    @property
    def internal_name(self):
        return 'JsonField'


class CommaSeperatedField(Field):
    def __init__(self, max_length: int = None):
        super().__init__(max_length=max_length)

    @property
    def internal_name(self):
        return 'CommaSeperatedField'

    def _to_python_object(self, value):
        values = detect_object_in_string(value)
        if not isinstance(values, list):
            attrs = {
                'value': value,
                't': self.__class__.__name__,
                'type1': type(value),
                'type2': self._dtype,
                'name': self.field_name
            }
            raise ValidationError(LazyFormat(
                self._validation_error_message, **attrs))
        return ','.join(map(lambda x: str(x), values))

    def resolve(self, values: List[Any]):
        if isinstance(values, str):
            values = detect_object_in_string(values)

        if not isinstance(values, (list, tuple)):
            raise TypeError(
                'The values parameter should be of type str, list or tuple.')

        container = ','.join(map(lambda x: str(x), values))
        self._cached_result = self._to_python_object(container)


class RegexField(Field):
    def __init__(self, pattern: str, group: int = 0, output_field: Field = None, **kwargs):
        self.pattern = re.compile(pattern)
        self.group = group
        self.output_field = output_field
        super().__init__(**kwargs)

    @property
    def internal_name(self):
        return 'RegexField'

    def resolve(self, value):
        value = self._run_validation(str(value))
        try:
            # If the value is None, this raises and
            # error, hence the try-catch function
            regexed_value = self.pattern.search(str(value))
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
    REP_TRUE = ['True', 'true', '1',
                'ON', 'On', 'on', True]

    REP_FALSE = ['False', 'false', '0',
                 'OFF', 'Off', 'off', False]

    def __init__(self, default=None, null=True):
        super().__init__(null=null, default=default)

    @property
    def internal_type(self):
        return bool

    @property
    def internal_name(self):
        return 'BooleanField'

    def _true_value_or_default(self, value):
        if isinstance(self.default, bool) and (value is None or value == Empty):
            return self.default
        return super()._true_value_or_default(value)

    def _to_python_object(self, value: Any):
        if not isinstance(value, bool):
            attrs = attrs = {
                'value': value,
                't': self.__class__.__name__,
                'type1': type(value),
                'type2': self.internal_type,
                'name': self.field_name
            }
            raise ValidationError(LazyFormat(
                self._validation_error_message, **attrs))
        return self.internal_type(value)

    def resolve(self, value: Any):
        if value in self.REP_TRUE:
            result = True
        elif value in self.REP_FALSE:
            result = False
        else:
            if value == '':
                value = Empty
            result = self._run_validation(value)
        self._cached_result = self._to_python_object(result)


class AutoField(Field):
    """Tracks the current IDs for a given model"""

    def __init__(self, auto_created=False):
        super().__init__()
        self.auto_created = auto_created
        self._tracked_id = 0

    @property
    def internal_name(self):
        return 'AutoField'

    def resolve(self):
        self._tracked_id = self._tracked_id + 1


class RelatedField(Field):
    is_relationship_field = True

    def __init__(self, model, relation_name=None):
        super().__init__()
        self.related_model = model
        self.related_name = relation_name
        self.reverse_related_name = None
        self.is_relationship_field = True

    def checks(self):
        errors = super().checks()
        if self.related_model is None:
            errors.extend([
                messages.ErrorMessage(
                    f"Related model cannot be None"
                )
            ])

        if not isinstance(self.related_name, str):
            errors.extend([
                messages.ErrorMessage(
                    f"Related name must be a string"
                )
            ])
        return errors

    def resolve(self, value):
        # The related model field should not
        # be resolving data directly so raise
        # an error if the user tries something
        # like model_name.add_value(related_field_name, value)
        raise Exception(
            f"A RelatedModel field cannot resolve data directly. Use {self.model._meta.model_name}.{self.field_name}.add_value(...) for example to add a value to the related model.")


# TODO: When the related field is set on the model
# we get [{'ages': [{'age': 30}], 'name': 'Kendall'}]
# for example. I think we should get instead
# [{'ages': {'age': 30}, 'name': 'Kendall'}] and create
# as many fields as the initial result that we
# are getting

# FIXME: Maybe find a better name for this field
# so that we know explicitly what it does

class RelatedModel(RelatedField):
    """Creates a relationship between two models. Does not
    keep track of the relationship between individual data
    and the related model. In other words, all the data
    from the related model will be included in the model
    
    >>> model.related_field.add_value("field_name", "...")
    """
    field_descriptor = OneToOneDescriptor

    def update_model_options(self, model, field_name):
        self.model = model
        self.field_name = field_name

        if self.related_name is None:
            related_model_name = self.related_model._meta.model_name
            self.related_name = f"{model._meta.model_name}_{related_model_name}"
            self.reverse_related_name = f"{related_model_name}_set"
            # This section we create the attribute that allows
            # us to get the data from the related model to the
            # one that created the relation. In that sense, if
            # we have model1.field where field being the
            # RelatedModelField, then we should be able to do
            # model2.field_set in reverse for model1
            setattr(self.related_model, self.reverse_related_name, self.model)

        # TODO: We should not be able to create a RelatedModel field
        # for the model that is a superclass of the model that wants
        # to create the relationship

        setattr(model, field_name, self.field_descriptor(self))
        model._meta.add_field(self.field_name, self)
