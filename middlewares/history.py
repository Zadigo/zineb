import datetime
import secrets
from collections import deque
from io import FileIO


class History:
    registry = deque()
    _current_token = secrets.token_hex(nbytes=10)

    def __call__(self, sender, url=None, tag=None, **kwargs):
        # print('History', sender, kwargs)
        buffer = FileIO('history', mode='a+')
        data = f"{self.timestamp} - {tag}: {url} [{self._current_token}]"
        buffer.write(bytes(data.encode('utf-8')))
        buffer.write(b'\n')
        buffer.close()

        self.create_request_record(url)

    @property
    def timestamp(self):
        return datetime.datetime.now().timestamp()

    def create_request_record(self, url):
        self.registry.append(('request', self.timestamp, url, self._current_token))

    def compile_statistics(self):
        number_of_items = len(self.registry)
        number_of_requests = filter(lambda x: 'request' in x, self.registry)
        return dict(sent=number_of_items, requests=len(number_of_requests))


class Job:
    def __call__(self, sender, **kwargs):
        pass

    def output_state(elf):
        pass
