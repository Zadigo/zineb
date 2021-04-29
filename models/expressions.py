from zineb.utils._html import deep_clean


class Expression:
    expressions = []

    def __str__(self):
        return f"{self.__class__.__name__}({' '.join(self.expressions)})"


class T:
    def __init__(self, expression, field_name):
        self.expression = expression
        self.html_page = None
        self.field_name = field_name
        self._cached_results = None

    def __call__(self):
        results = self.html_page.find_all(expression)
        def map_function(result): return deep_clean(result.string)
        self._cached_results = map(map_function, results)

    def __iter__(self):
        return next(self._cached_results)

    def __str__(self):
        return f'<{self.__class.__name__}>'
