from collections import OrderedDict
from functools import cached_property
from importlib import import_module

from zineb.logger import create_logger
from zineb.signals import signal

logger = create_logger('Middleware', to_file=True)

class Middleware:
    """
    Loads every middleware present in the project's
    settings file and in the user's settings file
    """
    settings = None
    module_registry = OrderedDict()

    def __init__(self, settings: dict={}):
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
                    try:
                        obj_instance = obj()
                    except Exception as e:
                        raise TypeError(f"{obj} was not loaded. {e.args[0]}")
                    self.loaded_middlewares.setdefault(key, obj_instance)
                    logger.info(f"Loaded middleware: {middleware}")

                    signal.connect(obj_instance)

    def get_middleware(self, name):
        if not self.loaded_middlewares:
            raise ValueError('Settings is not yet loaded')
        return self.loaded_middlewares.get(name, None)
