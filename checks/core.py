from collections import deque
from importlib import import_module
from typing import Callable


class GlobalMixins:
    _default_settings = None
    _errors = []


class ApplicationChecks(GlobalMixins):
    def __init__(self, default_settings=None):
        self._default_settings = default_settings or {}
        self._checks = deque()
    
    def run(self):
        modules = ['base', 'http']
        for module in modules:
            module = import_module(f'zineb.checks.{module}')
            
        for check in self._checks:
            new_errors = check(self._default_settings)
            if new_errors:
                self._errors.extend(new_errors)

    def register(self, tag: str = None):
        def inner(func: Callable):
            if not callable(func):
                raise TypeError('A system check should be a callable function to be registered')
            self._checks.append(func)
        return inner

checks_registry = ApplicationChecks()
