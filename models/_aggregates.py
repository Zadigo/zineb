import re
from zineb.http.responses import HTMLResponse
from zineb.models._expressions import Expressions

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
        return self.expressions.parse(self.expression)


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


# from bs4 import BeautifulSoup

# with open('tests/html/aggregates.html', 'r') as f:
#     soup = BeautifulSoup(f, 'html.parser')

# a = Aggregate(Max('div.ranking__text'), Sum('div.eugenie__text'), html_document=soup)
# print(Max('div.ranking__text'))
