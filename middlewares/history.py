from collections import deque
import datetime


class History:
    registry = deque()

    def __call__(self, sender, **kwargs):
        print('History', sender, kwargs)
        # name = kwargs.get('name')
        # if name == 'request':
        #     url = kwargs.get('url')
        #     self.create_request_record(url)

    @property
    def timestamp(self):
        return datetime.datetime.now().timestamp()

    def create_request_record(self, url):
        self.registry.append(('request', self.timestamp, url))

    def compile(self):
        number_of_items = len(self.registry)
        number_of_requests = filter(lambda x: 'request' in x, self.registry)
        return dict(sent=number_of_items, requests=len(number_of_requests))
