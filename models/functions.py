import datetime
from typing import Union

class Function:
    _cached_result = None

    def __str__(self):
        return str(self._cached_result)

    def resolve(self):
        raise NotImplemented('Subclasses should implement funciton resolution.')


class Extract(Function):
    date_element = 'year'

    def __init__(self, date: Union[str, datetime.datetime],
                 date_format: str = '%Y-%M-%d'):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, date_format)
        self._cached_result = date

    def resolve(self):
        allowed = ['month', 'day', 'year']
        if not self.date_element in allowed:
            raise ValueError(f"Can only extract {', '.join(allowed)} from date.")
        self._cached_result = getattr(self._cached_result, self.date_element)


class ExtractYear(Extract):
    date_element = 'year'


class ExtractMonth(Extract):
    date_element = 'month'


class ExtractDay(Extract):
    date_element = 'day'


class Lower(Function):
    def __init__(self, value):
        self._cached_result = value

    def resolve(self):
        self._cached_result = self._cached_result.lower()


class Upper(Function):
    def __init__(self, value):
        self._cached_result = value

    def resolve(self):
        self._cached_result = self._cached_result.upper()


class Replace:
    pass


class Left:
    def __init__(self, value):
        self._cached_result = value

    def resolve(self):
        self._cached_result = self._cached_result[:1][0]
