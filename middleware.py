import inspect
from importlib import import_module

from zineb.logger import logger
from zineb.settings import settings


class Middleware:
    """
    Loads every middleware present in the project's
    settings file and in the user's settings file
    """
    
    def __init__(self):
        self.middlewares = {}

        for middleware in settings.MIDDLEWARES:
            module_to_load, klass = middleware.rsplit('.', 1)
            try:
                module = import_module(module_to_load)
            except:
                raise ImportError('Middleware with path does not exist')
                                    
            for name, klass in inspect.getmembers(module, inspect.isclass):
                try:
                    instance = klass()
                except Exception as e:
                    raise TypeError(f"{klass} was not loaded. {e.args[0]}")
                else:
                    self.middlewares[name] = instance
                    
                logger.instance.info(f"Loaded middleware: {middleware}")
