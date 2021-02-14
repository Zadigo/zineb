class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)


class FieldError(Exception):
    def __init__(self, field_name, available_fields):
        msg = (f"The field ({field_name}) is not present on your model. "
        f"Available fields are: {', '.join(available_fields)}")
        super().__init__(msg)


class ParserError(Exception):
    def __init__(self):
        msg = (f"You should provide one of html_document, html_tag or HTMLResponse "
            "object to the model in order to resolve fields with a "
            "value from the HTML document")
        super().__init__(msg)
