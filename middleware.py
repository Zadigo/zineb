"""
Middlewares are pieces of codes that will be executed
before or after certain sequences of the Zineb spider.
"""

from collections import OrderedDict
from functools import cached_property
from importlib import import_module

from zineb.utils.general import create_logger


class Middleware:
    """
    Loads the middlewares registered in the
    settings.py file
    """
    settings = None

    def __init__(self):
        self.logger = create_logger(self.__class__.__name__)

        middlewares = []
        if self.settings is not None:
            middlewares = self.settings.get('MIDDLEWARES', [])
        self.middlewares = middlewares
        self.loaded_middlewares = OrderedDict()

    def _check_settings(self):
        if self.settings is not None:
            self.middlewares = self.settings.get('MIDDLEWARES')

    @cached_property
    def _load(self):
        self._check_settings()
        if self.middlewares:
            for middleware in self.middlewares:
                module_to_load, klass = middleware.rsplit('.', 1)
                module = import_module(module_to_load)
                module_dict = module.__dict__

                for key, obj in module_dict.items():
                    if key == klass:
                        self.loaded_middlewares.setdefault(key, obj)
                        self.logger.info(f"Loaded middleware: {middleware}")
