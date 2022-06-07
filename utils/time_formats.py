import datetime

import pytz
from zineb.settings import settings


def now():
    """Return the current date using the current
    application time zone setting"""
    timezone = pytz.timezone(settings.TIME_ZONE)
    current_date = datetime.datetime.now(tz=timezone)
    return current_date
