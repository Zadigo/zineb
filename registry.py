import os
import threading
import warnings
from collections import OrderedDict
from functools import lru_cache
from typing import Type

from pydispatch import dispatcher

from zineb import global_logger
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
        return self.spiders.values()

    def check_spiders_ready(self):
        if not self.spiders:
            raise ValueError(("Spiders are not yet loaded or "
            "there are no registered ones."))

    def check_spider_exists(self, name):
        return name in self.spiders.keys()

    def get_spider(self, spider_name: str) -> Type[SpiderConfig]:
        self.check_spiders_ready()
        try:
            return self.spiders[spider_name]
        except KeyError:
            global_logger.logger.error((f"The spider with the name '{spider_name}' does not "
            f"exist in the registry. Available spiders are {', '.join(self.spiders.keys())}. "
            f"If you forgot to register {spider_name}, check your settings file."), stack_info=True)
            raise

    def populate(self, project_spiders_module):
        """
        Definition that populates the registry
        with the spiders that were registered
        in the `SPIDERS` variable in the
        settings.py file

        Parameter
        ---------

            project_spiders_module (Module): the `spiders.py` module of the project
        """
        from zineb.settings import lazy_settings, settings

        for spider in settings.SPIDERS:
            config = SpiderConfig(spider, project_spiders_module)
            self.spiders[spider] = config

        settings.REGISTRY = self

        # Load all the middlewares once everything
        # is setup and ready to run
        middlewares = Middleware(settings=settings)
        middlewares._load

        signal.send(dispatcher.Any, self, spiders=self)

    def run_all_spiders(self):
        spiders = self.get_spiders()
        if not spiders:
            warnings.warn("There are no registered spiders in your project. If you created spiders, register them within the SPIDERS variable of your settings.py file.", Warning, stacklevel=0)
        else:
            for spider_config in spiders:
                try:
                    spider_config.run()
                except Exception:
                    # raise TypeError(f"Could not start {spider_config}. Is the configuration correct?")
                    new_logger = global_logger(name=self.__class__.__name__, to_file=True)
                    new_logger.error(f"Could not start {spider_config}. Did you use the correct class name?")
                else:
                    # Send a signal to all applications that might
                    # be interested that the spiders have started
                    # successfully
                    signal.send(dispatcher.Any, self)

registry = Registry()
