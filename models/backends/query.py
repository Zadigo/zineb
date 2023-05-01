from functools import cached_property
import importlib
from zineb.utils.module_loader import import_from_module

class Join:
    def as_xpath(self):
        pass


class Where:
    def as_xpath(self):
        pass


class Expressions:
    EQ = '='
    LT = '<'
    LTE = '<='
    GT = '>'
    GTE = '>='
    
    @staticmethod
    def resolve_value_part(subexpression):
        if '=' in subexpression:
            operator, value = subexpression.split('=', maxsplit=1)
            return operator, value
        return subexpression

    def resolve_subexpression(self, subexpression):
        if '__' in subexpression:
            attr, params = subexpression.split('__', maxsplit=1)
            operator, value = self.resolve_value_part(params)
            return attr, operator, value

    def resolve_expression(self, expression):
        # When __ in expression, we're dealing
        # with a conditional expression
        if '__' in expression:
            lhv, rhv = expression.split('__', maxsplit=1)
            conditions = self.resolve_subexpression(rhv)
            return lhv, conditions
        else:
            # When we have a simple string,
            # build the equivalent conditional
            # expression as a tuple
            return expression, (None, None, None)


class Query(Expressions):
    compiler = 'XPathCompiler'

    def __init__(self, request=None):
        self.request = request
        # Each queryset should contain the xpath
        # bit created from the chain .find_all('div').find('div')
        # would have xpath_bit = "//div[1]" or "//div[first()]"
        # or .find(div__class="kendall").text
        # would be "//div[first()]/text()"
        self.xpath_bit = None
        self.where_object = Where()

    def __str__(self):
        return ''

    @cached_property
    def html_content(self):
        return self.request.html_response.cached_response.content
    
    def get_compiler(self, using=None):
        compiler_path = f'zineb.models.backends.compiler.{self.compiler}'
        compiler = import_from_module(compiler_path)
        return compiler

    def clone(self):
        pass


    def get_initial_alias(self):
        return ['//']

    def combine(self):
        pass


class ResultItarable:
    def __init__(self, queryset):
        self.queryset = queryset

    def __iter__(self):
        compiler = self.queryset.query.get_compiler()
        result = compiler.execute_xpath()
        for item in result:
            yield item


class Queryset:
    def __init__(self, request):
        self.request = request
        self.query = Query(request)
        self._result_cache = None
        self._iterable_class = ResultItarable

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)

    def __len__(self):
        self._fetch_all()
        return len(self._result_cache)

    def _fetch_all(self):
        if self._result_cache is None:
            return self._iterable_class(self)

    def find(self, tag):
        pass

    def find_all(self, *args, **kwargs):
        return Queryset(self.request)

    def exists(self):
        pass

    def tables(self, *args, **kwargs):
        pass

    def count(self):
        pass


# from zineb.http.request import HTTPRequest
# r = HTTPRequest('http://example.com')
# r._send()
# q = Queryset(r)
# elements = q.find_all(body__class__eq='example')
# print(elements)

e = Query()
# r = e.resolve_expression('body__class__eq=example')
r = e.resolve_expression('body')
print(r)
