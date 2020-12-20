import datetime
import secrets
import pandas
from io import BytesIO

from bs4.element import Tag as beautiful_soup_tag
from PIL import Image
from w3lib.html import (replace_escape_chars, replace_tags,
                        strip_html5_whitespace)
from w3lib.url import is_url
from zineb.http.request import HTTPRequest
from zineb.utils.html import deep_clean


class Field:
    field_name = None
    field_tag_or_tags = None
    cached_result = None
    dtype = pandas.StringDtype

    _instance = None

    def __repr__(self):
        return f"{self.__class__.__name__}(data='{self.cached_result})'"

    def _check_type(self, value, object_to_check_against, message, enforce=True):
        result = isinstance(value, object_to_check_against)
        if not result:
            if enforce:
                raise TypeError(message)
            return result
        return value

    @staticmethod
    def _resolve_soup_object(obj):
        try:
            return obj.text
        except AttributeError:
            raise
        
    def resolve(self, value):
        if isinstance(value, (int, float)):
            return value

        if isinstance(value, beautiful_soup_tag):
            value = self._resolve_soup_object(value)

        if value is not None:
            cleaned_text = replace_escape_chars(strip_html5_whitespace(value))

            # On the first encounter of anything that
            # represents tags, just replace these elements
            # immediately and break
            tags = ['<', '>']
            for tag in tags:
                if tag in cleaned_text:
                    cleaned_text = replace_tags(cleaned_text)
                    break
            # return self.clean_in_between_spaces(cleaned_text)
            return deep_clean(value)
        return None

    def clean_in_between_spaces(self, text):
        """
        Despite the surface cleaning, there are certain texts
        that still contain white spaces between the words

        Example
        -------

                'Kendall        Jenner' -> 'Kendall Jenner'

        Parameters
        ----------

                text (str): a text to clean

        Returns
        -------

                str: a deep cleaned text
        """
        try:
            words = text.split(' ')
        except:
            return text
        else:
            clean_text = list(filter(lambda x: x != '', words))
            return ' '.join(clean_text)


class UrlField(Field):
    field_name = 'url'
    field_tag_or_tags = 'a'

    def __init__(self, text=None, fragment=None, nofollow=None):
        self.url = None
        self.text = text
        self.fragment = fragment
        self.nofollow = nofollow
        self.valid = False

    def __eq__(self, obj_to_compare):
        logic = [
            self.url == obj_to_compare.url,
            self.text == obj_to_compare.text,
            self.fragment == obj_to_compare.fragment,
            self.nofollow == obj_to_compare.nofollow
        ]
        return all(logic)

    def __hash__(self):
        return hash(
            (self.url, self.fragment, self.text, self.nofollow)
        )
        
    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url})"

    def resolve(self, url):
        result = self._check_type(
            url, str, 'Link should be of type string'
        )
        self.cached_result = super().resolve(result)
        self.valid = is_url(self.cached_result)
        return self.cached_result


class ImageField(UrlField):
    field_name = 'img'
    field_tag_or_tags = 'img'

    def __init__(self, download_to=None, download=False, as_thumnail=None):
        self.download = download
        self.download_to = download_to
        self.as_thumbnail = as_thumnail
        self.image_data = None
        self.metadata = {}

    def resolve(self, url):
        super().resolve(url)
        if self.download and self._instance is not None:
            request = HTTPRequest(self.cached_result)
            request._send()

            self.image_data = BytesIO(request._http_response.content)
            image = Image.open(self.image_data)
            self.metadata.update(
                {
                    'width': image.size,
                    'height': image.width,
                    'mode': image.mode
                }
            )

            if self.as_thumbnail:
                new_image = image.copy()
                return new_image.thumbnail(200)

            if self.download:
                if self.download_to is None:
                    self.download_to = f'{secrets.token_hex(nbytes=5)}.jpg'
                image.save(self.download_to)
        return self.cached_result


class CharField(Field):
    field_name = 'char'
    field_tag_or_tags = ['p']

    def resolve(self, text):
        text = super().resolve(text)
        self.cached_result = self._check_type(
            text, str, 'Text should be of type string'
        )
        return self.cached_result


class TextField(CharField):
    field_name = 'text'
    field_tag_or_tags = 'p'

    def resolve(self, text):
        result = super().resolve(text)
        return replace_tags(result)


class NameField(CharField):
    field_name = 'name'

    def resolve(self, text):
        result = super().resolve(text)
        self.cached_result = result.lower().title()
        return self.cached_result


class DateField(Field):
    field_name = 'date'
    dtype = pandas.DatetimeTZDtype

    def __init__(self, date_format, date_type='en'):
        self.date_format = date_format
        self.date_type = date_type
    
    def resolve(self, date, as_python_obj=False):
        date = super().resolve(date)
        result = datetime.datetime.strptime(
            date, self.date_format
        )
        if as_python_obj:
            return result
        else:
            self.cached_result = f"{result.year}-{result.month}-{result.day}"
            return self.cached_result


class AgeField(DateField):      
    field_name = 'age'
    dtype = pandas.Int64Dtype

    def resolve(self, date):
        date_obj = super().resolve(date, as_python_obj=True)
        current_date = datetime.datetime.now().date()
        return current_date.year - date_obj.year


class IntegerField(Field):
    field_name = 'number'
    dtype = pandas.Int64Dtype

    def resolve(self, value):
        result = super().resolve(value)
        self.cached_result = self._check_type(
            int(result), int, 'Value should be of type int'
        )
        return self.cached_result


class Function(Field):
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
    def __init__(self, field,  *methods, output_field=None):
        self.filtered_methods = []
        self.output_field = None

        for method in methods:
            if not callable(method):
                raise TypeError('You should provide a list of functions')
            self.filtered_methods.append(method)

    def resolve(self, value):
        self.cached_result = super().resolve(value)

        cached_result = None
        for method in self.filtered_methods:
            if cached_result is not None:
                cached_result = method(cached_result)
            else:
                cached_result = method(self.cached_result)

        if self.output_field:
            cached_result = self.output_field.resolve(
                self.cached_result
            )

        self.cached_result = cached_result
        return self.cached_result


class SmartField(Field):
    def resolve(self, value):
        result = super().resolve(value)
        if result.isnumeric() or result.isdigit():
            return IntegerField().resolve(value)

        if result.startswith('http'):
            return UrlField().resolve(result)

        if isinstance(value, str):
            return CharField().resolve(value)
        return result
        

class ArrayField(Field):
    def __init__(self, output_field=None):
        self.output_field = output_field
        if self.output_field is None:
            self.output_field = CharField()

    def resolve(self, values):
        values = self._check_type(values, list, 'Value should be of type list')
        resolved_values = []
        for value in values:
            resolved_values.append(
                self.output_field.resolve(value)
            )
        return resolved_values


class CommaSeperatedField(Field):
    def resolve(self, values):
        self._check_type(values, list, 'Values should of type list')
        output_as = CharField()
        resolved_values = []
        for value in values:
            resolved_values.append(
                output_as.resolve(value)
            )
        self.cached_result = ','.join(resolved_values)
        return self.cached_result

