from collections import OrderedDict
from functools import cached_property
from importlib import import_module

from zineb.signals import signal
from zineb.logger import create_logger

logger = create_logger('Middleware')

class Middleware:
    """
    Loads every middleware present in the project's
    settings file and in the user's settings file
    """
    settings = None
    module_registry = OrderedDict()

    def __init__(self, settings={}):
        self.project_middlewares = settings.get('MIDDLEWARES', [])
        self.loaded_middlewares = OrderedDict()

    @property
    def middlewares_by_name(self):
        return self.module_registry.keys()

    @cached_property
    def _load(self):
        for middleware in self.project_middlewares:
            module_to_load, klass = middleware.rsplit('.', 1)
            module = import_module(module_to_load)
            module_dict = module.__dict__

            _, name = module.__name__.rsplit('.', maxsplit=1)
            self.module_registry[name] = module

            # Now load each class object specified
            # in the middleware list individually
            for key, obj in module_dict.items():
                if key == klass:
                    self.loaded_middlewares.setdefault(key, obj)
                    logger.info(f"Loaded middleware: {middleware}")
