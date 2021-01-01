from w3lib.url import urlparse

class GlobalMixins:
    _default_settings = None
    _errors = []


class ApplicationChecks(GlobalMixins):
    def __init__(self, default_settings=None):
        self._default_settings = default_settings or {}

    def run(self):
        for check in self._checks():
            new_errors = check()
            if new_errors:
                self._errors.extend(new_errors)

    def register(self, tag=None):
        def inner(func):
            if not callable(func):
                raise TypeError
            self.checks.append(func)
        return inner

checks_registry = ApplicationChecks()
