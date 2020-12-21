class NoRequestWarning(UserWarning):
    pass


class ValidationError(Exception):
    def __init__(self, message, *args):
        super().__init__(message, *args)


class FieldError(Exception):
    pass
