class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class FieldError(Exception):
    def __init__(self, field_name, available_fields):
        msg = (f"The field '{field_name}' is not present on your model. "
        f"Available fields are: {', '.join(available_fields)}")
        super().__init__(msg)


class ParserError(Exception):
    def __init__(self):
        msg = (f"You should provide one of html_document, html_tag or HTMLResponse "
            "object to the model in order to resolve fields with a "
            "value from the HTML document")
        super().__init__(msg)


class CommandRequiresProjectError(Exception):
    def __init__(self, command):
        msg = (f"'{command}' was called outside of a project scope.")
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
    def __init__(self):
        super().__init__('Your project is not properly configured.')


class SpiderExistsError(Exception):
    def __init__(self, name: str):
        super().__init__(f"'{name}' does not exist in the registry. "
        f"Did you create '{name}' in your spiders module?")


class ResponseFailedError(Exception):
    def __init__(self):
        super().__init__("Zineb will not be able to generate a BeautifulSoup object from the response. "
        "This is due to a response with a fail status code or being None.")


class RequestAborted(Exception):
    pass
