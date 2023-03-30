import inspect
from importlib import import_module

from zineb.logger import logger
from zineb.settings import settings
from zineb.utils.formatting import LazyFormat


class Middleware:
    """
    Loads every middleware present in the
    settings file
    """

    def __init__(self):
        self.middlewares = {}

        for middleware in settings.MIDDLEWARES:
            module_to_load, klass = middleware.rsplit('.', 1)
            try:
                module = import_module(module_to_load)
            except:
                message = LazyFormat(
                    "Middleware with path '{path}' does not exist", path=middleware)
                raise ImportError(message)

            for name, klass in inspect.getmembers(module, inspect.isclass):
                try:
                    instance = klass()
                except Exception as e:
                    raise TypeError(
                        f"{klass} could not be instantiated. {e.args[0]}")
                else:
                    if hasattr(klass, 'process_middleware') and name != 'MiddlewareMixin':
                        self.middlewares[name] = instance
                        logger.instance.info(
                            f"Loaded middleware: {middleware}")

    def run_middlewares(self, spider, request):
        """Runs all the middlewares on the
        the actual request"""
        for middleware in self.middlewares.values():
            middleware(request)
