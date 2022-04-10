from itertools import chain 

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class FieldError(Exception):
    def __init__(self, field_name, available_fields, model_name=None):
        msg = (f"The field '{field_name}' is not present on your model. "
        f"Available fields are: {', '.join(available_fields)}")
        super().__init__(msg)


class ParserError(Exception):
    def __init__(self):
        msg = (f"You should provide one of html_document, html_tag or HTMLResponse "
            "object to the model in order to resolve fields with a "
            "value from the HTML document")
        super().__init__(msg)


class ProjectExistsError(FileExistsError):
    def __init__(self):
        super().__init__('The project path does not exist.')


class ProjectNotConfiguredError(Exception):
    def __init__(self):
        super().__init__(("You are trying to run a functionnality that requires "
        "you project to be fully configured via your settings file."))


class ModelNotImplementedError(Exception):
    def __init__(self, message: str=None):
        super().__init__(("Conditional (When), aggregate (Add, Substract, Multiply, Divide)"
        f" functions should point to a model. {message}"))


class ModelExistsError(Exception):
    def __init__(self, name: str):
        super().__init__((f"Model '{name}' is already registered."))


class ImproperlyConfiguredError(Exception):
    def __init__(self, *args):
        message = 'Your project is not properly configured.'
        if args:
            additional_errors = ' / '.join(chain(*args))
            message = message + ' Identified the following errors: ' + additional_errors
        super().__init__(message)


class SpiderExistsError(Exception):
    def __init__(self, name: str):
        super().__init__(f"'{name}' does not exist in the registry. "
        f"Did you create '{name}' in your spiders module?")


class ResponseFailedError(Exception):
    def __init__(self, *args):
        # FIXME: Show additional errors that
        # would come from the HTTPRequest
        super().__init__("The request was not sent either"
        " due to a response with a fail status code or being None.")

class RequestAborted(Exception):
    pass


class ModelConstraintError(Exception):
    def __init__(self, field_name, value):
        super().__init__(f"Constraint not respected on '{field_name}'. '{value}' already present in the model.")


class RequiresProjectError(Exception):
    def __init__(self):
        super().__init__('Project scope is required for this command.')


class ConstraintError(Exception):
    def __init__(self):
        super().__init__('A constraint error was raised on the given model')
