import re
from zineb.http.responses import HTMLResponse

class Expressions:
    parser = None

    def __init__(self, html_document=None, html_tag=None, response=None):
        self.html_document = html_document
        self.html_tag = html_tag
        self.response = response
        self.parser = self._choose_parser()

    def __call__(self, html_document=None, html_tag=None, response=None):
        self.__init__(html_document=html_document, html_tag=html_tag, response=response)

    @staticmethod
    def _expression_resolver(expression):
        try:
            tag_name, pseudo = expression.split('__', 1)
        except:
            # If no pseudo is passed, just use the default
            # text one by appending it to the expression
            expression = expression + '__text'
            tag_name, pseudo = expression.split('__', 1)

        matched_elements = re.search(r'(?P<tag>\w+)(?P<marker>\.|\#)?(?P<attr>\w+)?', tag_name)
        named_elements = matched_elements.groupdict()

        attrs = {}
        markers = {'.': 'class', '#': 'id'}
        marker = named_elements.get('marker', None)
        if marker is not None:
            try:
                named_marker = markers[marker]
            except:
                raise KeyError('Marker is not a recognized marker')
            else:
                attrs.update({named_marker: named_elements.get('attr')})
        return named_elements.get('tag'), pseudo, attrs

    def _resolve_pseudo(self, pseudo, tag):
        allowed_pseudos = ['text', 'href', 'src']
        if pseudo not in allowed_pseudos:
            raise ValueError('Pseudo is not an authorized pseudo')

        if pseudo == 'text':
            return getattr(tag, 'text')
        else:
            return tag.attrs.get(pseudo)

    def _choose_parser(self):
        # In case we get both the HTML document
        # and a tag, use the most global element
        # in order to have better results
        if self.html_document and self.html_tag:
            return self.html_document

        if self.html_tag is not None:
            return self.html_tag

        if self.html_document is not None:
            return self.html_document

        if self.response is not None:
            if not isinstance(self.response, HTMLResponse):
                raise TypeError(("The request object should be a "
                "zineb.response.HTMLResponse object"))
            return self.response.html_document

    def resolve(self, expression, many=True):
        tag_name, pseudo, attrs = self._expression_resolver(expression)
        if many:
            tags = self.parser.find_all(tag_name, attrs=attrs)
            results = [self._resolve_pseudo(pseudo, tag) for tag in tags]
        else:
            tag = self.parser.find(tag_name, attrs=attrs)
            results = [self._resolve_pseudo(pseudo, tag)]
        return results


class Function:
    expressions = Expressions()

    def __init__(self, expression):
        self.expression = expression
        self._cached_values = []
        self.incorrect_values = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.__class__.__name__}({self._cached_values})"

    def __contains__(self, value):
        return value in self.calculate()

    def _remap_values(self):
        def remap(x):
            if x.isnumeric():
                return True
            self.incorrect_values.append()
            return False
        numeric_values = filter(remap, self._cached_values)
        return map(lambda x: int(x), numeric_values)

    def calculate(self):
        return self.expressions.resolve(self.expression)


class Sum(Function):
    def calculate(self):
        self._cached_values = super().calculate()
        return sum(self._remap_values())


class Avg(Function):
    def calculate(self):
        sum_instance = Sum(self.expression)
        return sum_instance.calculate() / len(self._cached_values)


class Max(Function):
    def calculate(self):
        return max(super().calculate())


class Min(Function):
    def calculate(self):
        return min(super().calculate())


class Aggregate:
    _cached_calculations = []

    def __init__(self, *functions, html_document=None, response=None):
        self.registered_expressions = []

        for function in functions:
            if not isinstance(function, (Sum, Avg, Min, Max)):
                raise TypeError('Function should be one of Sum and Avg')
            function.expressions(html_document=html_document, response=response)
            self.registered_expressions.append(
                f"{function.expression}__{function.__class__.__name__.lower()}"
            )
            self._cached_calculations.extend([function.calculate()])

    def __repr__(self):
        return self._cached_calculations

    def __str__(self):
        return_values = {}
        for i in range(0, len(self.registered_expressions)):
            return_values.update({self.registered_expressions[i]: self._cached_calculations[i]})
        # return str(self._cached_calculations)
        return str(return_values)


class When:
    expressions = Expressions()

    def __init__(self,  if_condition=None, then_condition=None):
        pass

    def resolve(self, expression):
        results = self.expressions.resolve(expression)
        return filter(lambda x: x, results)


from bs4 import BeautifulSoup

with open('tests/html/aggregates.html', 'r') as f:
    soup = BeautifulSoup(f, 'html.parser')

a = Aggregate(Max('div.ranking__text'), Sum('div.eugenie__text'), html_document=soup)
print(Max('div.ranking__text'))
