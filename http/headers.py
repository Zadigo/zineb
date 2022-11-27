import datetime
from collections import OrderedDict


class ResponseHeaders(OrderedDict):
    __slot__ = ()

    def __init__(self, response_headers: dict):
        date = response_headers.get('Date', None)
        if date is not None:
            formatted_date = self._transform_date_to_python(date)
            response_headers.update({'Date': formatted_date})

        last_modified = response_headers.get('Last-Modified', None)
        if last_modified is not None:
            formatted_date = self._transform_date_to_python(last_modified)
            response_headers.update({'Last-Modified': formatted_date})

        expires = response_headers.get('Expires', None)
        if expires is not None:
            expires = self._transform_date_to_python(expires)
            response_headers.update({'Expires': expires})

        super().__init__(**self._refix(response_headers))
        
    @property
    def is_json_response(self):
        content_type = self.get('content-type', None)
        return 'application/json' in content_type

    def _transform_date_to_python(self, d):
        if isinstance(d, datetime.datetime):
            return d
        try:
            # This should not be a blocking element.
            # If we cannot convert some sort of date,
            # just return None
            return datetime.datetime.strptime(d, '%a, %d %b %Y %H:%M:%S GMT')
        except:
            return None

    def _refix(self, headers: dict):
        """Normalizes the header names by transforming
        them to lower case"""
        intital_keys = headers.keys()
        keys = sorted(intital_keys)

        refixed_headers = {}
        for key in keys:
            refixed_headers.update({key: headers[key]})

        final_headers = OrderedDict()
        for key, value in refixed_headers.items():
            final_headers.update({key.lower(): value})
        return final_headers
