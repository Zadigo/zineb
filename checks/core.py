from collections import OrderedDict, deque
from importlib import import_module
from typing import Callable

from zineb.settings import settings as global_settings


class GlobalMixins:
    _default_settings = None
    _errors = []
    _MODULES = OrderedDict()


class ApplicationChecks(GlobalMixins):
    def __init__(self, default_settings={}):
        self._default_settings = (
            default_settings or 
            global_settings
        )
        self._checks = deque()
    
    def run(self):
        # We have to preload all the modules
        # in order for the checks to be correctly
        # registered within the ApplicationChecks class
        modules = ['base', 'http']
        for module in modules:
            module = import_module(f'zineb.checks.{module}')
            path = getattr(module, '__file__')

            filename = getattr(module, '__name__')
            filename = filename.rpartition('.')[-1]
            self._MODULES.setdefault(filename, [path, module])

        self.check_settings_integrity()
            
        for check in self._checks:
            new_errors = check(self._default_settings)
            if new_errors:
                self._errors.extend(new_errors)

        if self._errors:
            pass

    def check_settings_integrity(self):
        """
        Verifies that certain values are present
        in the project before starting the project


        Raises:
            ValueError: [description]
        """
        required_values = ['PROJECT_PATH', 'SPIDERS']
        keys = self._default_settings.keys()
        for value in required_values:
            if value not in keys:
                raise ValueError(f"The following settings {value} is required in your settings file.")

        requires_list_or_tuples = ['SPIDERS', 'DOMAINS', 'MIDDLEWARES', 'USER_AGENTS', 'PROXIES', 'RETRY_HTTP_CODES']
        for item in requires_list_or_tuples:
            value = getattr(self._default_settings, item)
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"{item} in settings.py should contain a list or a tuple ex. {item} = []")

        # If Zineb is called from a project configuration
        # we should automatically assume that is a path
        PROJECT_PATH = getattr(self._default_settings, 'PROJECT_PATH', None)
        if PROJECT_PATH is None:
            raise ValueError(("PROJECT_PATH is empty. If you are using "
            "Zineb outside of a project, call .configure(**kwargs)"))

    def register(self, tag: str = None):
        def inner(func: Callable):
            if not callable(func):
                raise TypeError('A system check should be a callable function to be registered')
            self._checks.append(func)
        return inner

checks_registry = ApplicationChecks()
