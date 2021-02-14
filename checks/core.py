from collections import deque


class GlobalMixins:
    _default_settings = None
    _errors = []


class ApplicationChecks(GlobalMixins):
    def __init__(self, default_settings=None):
        self._default_settings = default_settings or {}
        self._checks = deque()
    
    def run(self):
        for check in self._checks:
            new_errors = check(self._default_settings)
            if new_errors:
                self._errors.extend(new_errors)

    def register(self, tag=None):
        def inner(func):
            if not callable(func):
                raise TypeError('A system check should be a callable function to be registered')
            self._checks.append(func)
        return inner

checks_registry = ApplicationChecks()
