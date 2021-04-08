import os
import threading
from collections import OrderedDict
from functools import lru_cache
from typing import Type

from pydispatch import dispatcher

from zineb.middleware import Middleware
from zineb.signals import signal


class SpiderConfig:
    """
    Class that represents a spider and the different
    characteristics that it holds
    """

    def __init__(self, name: str, project_module):
        self.name = name
        
        # The root module of the project
        # ex. myproject.spiders
        self.module = project_module

        if not hasattr(self, 'label'):
            self.label = self.name.rpartition('.')[2]

        paths = list(getattr(self.module, '__path__', []))
        if not paths:
            filename = getattr(self.module, '__file__', None)
            if filename is not None:
                paths = [os.path.dirname(filename)]

        if len(paths) > 1:
            raise ValueError(
                "There are multiple modules trying to start spiders")

        if not paths:
            raise ValueError(
                "No spiders module within your project. Please create a 'spiders.py' module.")

        self.path = paths[0]

    def __str__(self):
        return f"<SpiderConfig(name={self.name})>"

    def __repr__(self):
        return self.__str__()

    def get_spider(self, name):
        return getattr(self.module, name)

    def run(self):
        self.get_spider(self.label)()
    

class Registry:
    """
    Registry that keeps in mind all the spiders
    that are created by the user and their
    configurations
    """
    def __init__(self, spiders={}):
        self.spiders = OrderedDict(**spiders)

    def __str__(self):
        return f"<{self.__class__.__name__}(spiders={len(self.spiders.keys())})>"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.spiders.values())

    def __contains__(self, name):
        return name in self.spiders.keys()

    @lru_cache(maxsize=1)
    def get_spiders(self):
        self.check_spiders_ready()
        return self.spiders.values()

    def check_spiders_ready(self):
        if not self.spiders:
            raise ValueError('Spiders are not loaded yet')

    def check_spider_exists(self, name):
        return name in self.spiders.keys()

    def get_spider(self, spider_name: str) -> Type[SpiderConfig]:
        self.check_spiders_ready()
        return self.spiders[spider_name]

    def populate(self, project_module):
        from zineb.settings import settings

        # Force the loading of the settings with
        # the user settings because the settings are
        # loaded before the all this code is run aka
        # zineb.settings.__init__. In that scenario,
        # the user settgins are not implemented
        settings(REGISTRY=None)
        for spider in settings.SPIDERS:
            config = SpiderConfig(spider, project_module)
            self.spiders[spider] = config

        settings.REGISTRY = self

        # Load all the middlewares once everything
        # is setup and ready to run
        middlewares = Middleware(settings=settings)
        middlewares._load

        signal.send(dispatcher.Any, self, spiders=self.spiders)

    def run_all_spiders(self):
        for spider_config in self.get_spiders():
            try:
                spider_config.run()
            except Exception:
                raise TypeError(f"Could not start {spider_config}. Is the configuration correct?")
            # Send a signal to all applications that might
            # be interested that the spiders have started
            # successfully
            signal.send(dispatcher.Any, self)

registry = Registry()
