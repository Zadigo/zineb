import datetime
from collections import deque


class History:
    registry = deque()

    def __call__(self, sender, **kwargs):
        print('History', sender, kwargs)

    @property
    def timestamp(self):
        return datetime.datetime.now().timestamp()

    def create_request_record(self, url):
        self.registry.append(('request', self.timestamp, url))

    def compile(self):
        number_of_items = len(self.registry)
        number_of_requests = filter(lambda x: 'request' in x, self.registry)
        return dict(sent=number_of_items, requests=len(number_of_requests))
