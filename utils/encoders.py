import six
import datetime
import decimal
import uuid
from json.encoder import JSONEncoder
from typing import Any, Type

from zineb.utils.formatting import LazyFormat


class DefaultJsonEncoder(JSONEncoder):
    """
    An encoder specially created to encode datetime
    objects or other specific Python representations
    """
    def default(self, obj):
        # Date/Time string spcifications at ECMA 262
        # https://ecma-international.org/ecma-262/5.1/#sec-15.9.1.15

        if isinstance(obj, datetime.datetime):
            representation = obj.isoformat()
            if representation.endswith('+00:00'):
                representation = representation[:-6] + 'Z'
            return representation

        if isinstance(obj, datetime.time):
            if datetime.timezone and datetime.timezone.is_aware(obj):
                raise ValueError('Cannot represent timezon-aware times.')
            return obj.isoformat()

        if isinstance(obj, datetime.date):
            return str(obj)

        if isinstance(obj, datetime.timedelta):
            return str(obj.total_seconds())

        if isinstance(obj, decimal.Decimal):
            return float(obj)

        if isinstance(obj, uuid.UUID):
            return str(obj)

        if isinstance(obj, bytes):
            return obj.decode()

        if hasattr(obj, 'tolist'):
            return obj.tolist()

        # Conversion for lists and tuples
        if hasattr(obj, '__getitem__'):
            convert_to = list if isinstance(obj, (list, tuple)) else dict
            try:
                return convert_to(obj)
            except Exception:
                raise
        
        if hasattr(obj, '__iter__'):
            return tuple(item for item in obj)

        return super().default(obj)


def convert_to_unicode(value: Any, encoding='utf-8', errors='strict'):
    """
    Return the unicode representation of a bytes object `text`.
    If the value is already a text, return it.
    """
    if isinstance(value, six.text_type):
        return value

    if not isinstance(value, (bytes, six.text_type)):
        raise TypeError(LazyFormat(('Value must be of type bytes, '
        'str or unicode. Got {value_type}'), value_type=type(value)))

    return value.decode(encoding, errors)
