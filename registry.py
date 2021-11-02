import os
import warnings
import threading
from collections import OrderedDict
from functools import lru_cache
from zineb.middleware import Middleware
from zineb import global_logger
from zineb.exceptions import SpiderExistsError


class SpiderConfig:
    """
    Class that represents a spider and its configurations
    via the `_meta` attribute.
    """

    def __init__(self, name: str, spiders_module):
        self.name = name
        
        # The root spiders module of the project
        # ex. myproject.spiders that contains
        # the spiders that we need to grab
        # when the get_spider is called
        self.MODULE = spiders_module

        if not hasattr(self, 'label'):
            self.label = self.name.rpartition('.')[2]

        paths = list(getattr(self.MODULE, '__path__', []))
        if not paths:
            filename = getattr(self.MODULE, '__file__', None)
            if filename is not None:
                paths = [os.path.dirname(filename)]

        if len(paths) > 1:
            raise ValueError("There are multiple modules "
            "trying to start spiders")

        if not paths:
            raise ValueError("No spiders module within your project. "
            "Please create a 'spiders.py' module.")

        self.path = paths[0]

    def __str__(self):
        return f"<SpiderConfig(name={self.name})>"

    def __repr__(self):
        return self.__str__()

    @lru_cache(maxsize=5)
    def get_spider(self, name):
        try:
            return getattr(self.MODULE, name)
        except AttributeError:
            raise SpiderExistsError(name)

    def run(self):
        """Runs the spider by calling the spider class
        which in return calls .start(...)"""
        spider = self.get_spider(self.label)
        # thread = threading.Thread(target=spider)
        # thread.daemon = True
        # thread.start()
        spider()
    

class Registry:
    """
    Registry that keeps in memory all the spiders
    that are created within a project and their
    current settings
    """
    def __init__(self, spiders={}):
        # As simple flat to check if the
        # register was populated (in other
        # words with .populate() was called)
        self.is_ready = False
        self.local_logger = global_logger.new(name=self.__class__.__name__, to_file=True)
        self.spiders = OrderedDict(**spiders)

    def __str__(self):
        return f"<{self.__class__.__name__}(spiders={len(self.spiders.keys())})>"

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.spiders.values())

    def __contains__(self, name):
        return name in self.spiders.keys()

    @property
    def has_spiders(self):
        return len(self.spiders.keys()) > 0

    @lru_cache(maxsize=1)
    def get_spiders(self):
        return self.spiders.values()

    def has_spider(self, name):
        return self.__contains__(name)

    def check_spiders_ready(self):
        if not self.has_spiders:
            raise ValueError(("Spiders are not yet loaded or "
            "there are no registered ones."))

    def check_spider_exists(self, name):
        return name in self.spiders.keys()

    def get_spider(self, spider_name: str) -> SpiderConfig:
        self.check_spiders_ready()
        try:
            return self.spiders[spider_name]
        except KeyError:
            self.local_logger.error((f"The spider with the name '{spider_name}' does not "
            f"exist in the registry. Available spiders are {', '.join(self.spiders.keys())}. "
            f"If you forgot to register {spider_name}, check your settings file."), stack_info=True)
            raise SpiderExistsError(spider_name)

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
        from zineb.settings import settings

        for spider in settings.SPIDERS:
            spider_config = SpiderConfig(spider, project_spiders_module)
            self.spiders[spider] = spider_config

        # Cache the registry since we don't want
        # to be populating this every single time
        # unless necessary
        settings.REGISTRY = self
        # TODO: Load all the middlewares once everything
        # is setup and ready to run
        # middlewares = Middleware(settings=settings)
        # middlewares._load

        # TODO:
        # signal.send(dispatcher.Any, self, spiders=self)
        self.is_ready = True

    def run_all_spiders(self):
        spiders = self.get_spiders()
        if not spiders:
            warnings.warn(("There are no registered spiders in your project. If you created spiders, "
            "register them within the SPIDERS variable of your "
            "settings.py file."), Warning, stacklevel=0)
        else:
            for spider_config in spiders:
                try:
                    spider_config.run()
                except Exception as e:
                    self.local_logger.critical((f"Could not start {spider_config}. "
                    "Did you use the correct class name?"), stack_info=True)
                    raise
                else:
                    # TODO:
                    # signal.send(dispatcher.Any, self)
                    pass


registry = Registry()
