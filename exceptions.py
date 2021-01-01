import warnings


class NoRequestWarning(UserWarning):
    pass


class StartUrlsWarning(SyntaxWarning):
    def __init__(self):
        super().__init__('No starting urls were specified')


class DomainOutOfBounds(UserWarning):
    def __init__(self, url, *args):
        message = 'The url does not'
        super().__init__(message)


class ValidationError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


class FieldError(Exception):
    pass
