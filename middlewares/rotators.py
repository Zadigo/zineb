import random
from collections import OrderedDict
from zineb.middlewares.mixins import MiddlewareMixin
from zineb.settings import settings


class RotatingProxy(MiddlewareMixin):
    """A class that rotates proxy adresses
    for each request"""

    def __init__(self):
        self.proxy_history = []

    def __call__(self, request):
        self.process_middleware(request)

    def process_middleware(self, request):
        if settings.PROXIES:
            proxy = random.choice(settings.PROXIES)
            proxy = dict(OrderedDict([proxy]))
            self.proxy_history.append(proxy)
            setattr(request, '_proxy', proxy)
            return proxy, request
        return None, request
