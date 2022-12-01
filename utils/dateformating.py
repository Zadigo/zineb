import datetime

from zineb.settings import settings
from zineb.utils.formatting import LazyFormat


def extract_date_from_string(value, field_name, date_parser=datetime.datetime.strptime, *formats):
    """Transform a date in a string into a datetime object
    
    >>> extract_date_from_string('2022-1-1', 'field_name')
    ... datetime.datetime.date('2022-1-1)
    """
    formats = set(getattr(settings, 'DEFAULT_DATE_FORMATS'))
    
    for format in formats:
        formats.add(format)

    for date_format in formats:
        try:
            # Test the date against the list of
            # date formats available in DEFAULT_DATE_FORMATS
            d = date_parser(value, date_format)
        except:
            d = None
            continue
        else:
            break

    if d is None:
        message = LazyFormat("Could not find a valid format for "
                             "date '{d}' on field '{name}'.", d=value, name=field_name)
        raise ValueError(message)

    return d.date()
