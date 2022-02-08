import os
import warnings
from collections import OrderedDict, deque
from importlib import import_module
from typing import Callable

from zineb.exceptions import ImproperlyConfiguredError, ProjectExistsError
from zineb.settings import settings as global_settings


DEFAULT_CHECKS_MODULES = (
    'base',
    'http'
)


class GlobalMixins:
    # _default_settings = None
    _errors = []
    _MODULES = OrderedDict()


class ApplicationChecks(GlobalMixins):
    def __init__(self):
        # self._default_settings = global_settings
        self._checks = deque()
    
    def run(self):
        # We have to preload all the modules
        # in order for the checks to be correctly
        # registered within this class
        for module in DEFAULT_CHECKS_MODULES:
            module = import_module(f'zineb.checks.{module}')

            path = getattr(module, '__file__')
            filename = getattr(module, '__name__')

            filename = filename.rpartition('.')[-1]
            self._MODULES.setdefault(filename, [path, module])

        self.check_settings_base_integrity()
            
        for func in self._checks:
            # new_errors = func(self._default_settings)
            new_errors = func()
            if new_errors:
                self._errors.extend(new_errors)

        for error in self._errors:
            warnings.warn(error, stacklevel=1)
            
        if self._errors:
            raise ImproperlyConfiguredError(self._errors)

    def check_settings_base_integrity(self):
        """
        Verifies that all the base variables (PROJECT_PATH, PROXIES...)
        are correctly implemented
        
        For example the PROXIES setting requires a tuple or list
        """
        required_values = ['PROJECT_PATH', 'SPIDERS']
        keys = global_settings.keys()
        for value in required_values:
            if value not in keys:
                raise ValueError(f"The following settings '{value}' are required in your settings file.")

        requires_list_or_tuple = ['SPIDERS', 'DOMAINS', 'MIDDLEWARES',
                                  'USER_AGENTS', 'PROXIES', 'RETRY_HTTP_CODES', 
                                  'DEFAULT_DATE_FORMATS']
        for item in requires_list_or_tuple:
            value = getattr(global_settings, item)
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"{item} in settings.py should contain a list or a tuple ex. {item} = []")

        # If Zineb is called from a project configuration
        # we should automatically assume that it is a path
        PROJECT_PATH = getattr(global_settings, 'PROJECT_PATH', None)
        if PROJECT_PATH is None:
            raise ValueError(("PROJECT_PATH is empty. If you are using "
            "Zineb outside of a project, call .configure(**kwargs)"))
        
        # Also make sure that the path is one that really
        # exists in case the user changes this variable
        # to a 'string' path [...] thus breaking the
        # whole thing
        if not os.path.exists(PROJECT_PATH):
            raise ProjectExistsError()

        # Also make sure that this is
        # a directory
        if not os.path.isdir(PROJECT_PATH):
            raise IsADirectoryError("PROJECT_PATH should be the project's directory")

    def register(self, tag: str = None):
        """Register a check on this class by using 
        this decorator on a custom function

        Example
        -------

            @register
            def some_check():
                pass
        """
        def inner(func: Callable):
            if not callable(func):
                raise TypeError('A system check should be a callable function to be registered')
            self._checks.append(func)
        return inner


checks_registry = ApplicationChecks()
register = checks_registry.register
