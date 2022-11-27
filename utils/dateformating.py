import datetime

from zineb.settings import settings
from zineb.utils.formatting import LazyFormat


def extract_date_from_string(value, field_name, date_parser=datetime.datetime.strptime, **formats):
    formats = set(getattr(settings, 'DEFAULT_DATE_FORMATS'))
    formats.add(date_format)

    for date_format in formats:
            try:
                d = date_parser(value, date_format)
            except:
                d = None
            else:
                if d:
                    break

    if d is None:
        message = LazyFormat("Could not find a valid format for "
                             "date '{d}' on field '{name}'.", d=value, name=field_name)
        raise ValueError(message)

    return d.date()
