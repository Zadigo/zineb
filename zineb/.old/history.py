import datetime
import secrets
from collections import deque, namedtuple
from hashlib import md5
from io import FileIO


class History:
    registry = deque()
    _current_token = secrets.token_hex(nbytes=10)

    def __call__(self, sender, url: str = None, tag: str = None, **kwargs):
        # buffer = FileIO('history', mode='a+')
        # tag = tag.lower()
        # data = f"{self.timestamp} - {tag}: {url} [{self._current_token}]"
        # buffer.write(bytes(data.encode('utf-8')))
        # buffer.write(b'\n')
        # buffer.close()
        
        self._create_token(self.timestamp, url, tag)
        self.create_request_record(url)

    @property
    def timestamp(self):
        current_date = datetime.datetime.now(tz=datetime.timezone.utc)
        return current_date.timestamp()

    def _create_token(self, *items):
        elements = '-'.join(str(item) for item in items)
        self._current_token = md5(elements.encode('utf-8')).hexdigest()

    def create_request_record(self, url):
        self.registry.append(('request', self.timestamp, url, self._current_token))

    def compile_statistics(self):
        number_of_items = len(self.registry)
        number_of_requests = filter(lambda x: 'request' in x, self.registry)
        # return dict(sent=number_of_items, requests=len(number_of_requests))
        statistics = namedtuple('Statistics', ['count', 'requests'])
        return statistics(number_of_items, number_of_requests)
