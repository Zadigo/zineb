from zineb.html_parser import nodes


class Iterable:
    def __iter__(self, instance, cls=None):
        expression = []
        items = self.compiler(instance)
        for result in items:
            yield result


# .filter(div__id="google") -> /body//div[@id="google"]
# .filter(div__id__eq="google") -> /body//div[@id="google"]
# .filter(div__id__ne="google") -> /body//div[not(@id, "google")]
# .filter(div__id__icontains="google") -> /body//div[contains(@id, "google") or contains(@id, "Google")]
# .filter(div__id__contains="google") -> /body//div[contains(@id, "Google")]
# .filter(div__id__gt="google") -> /body//div[]
# .filter(div__id__gte="google") -> /body//div[]
# .filter(div__id__lt="google") -> /body//div[]
# .filter(div__id__lte="google") -> /body//div[]
# .filter(div__id__lte="google") -> /body//div[]
# .filter(div__id__startswith="google") -> /body//div[starts-with(@id, "google")]
# .filter(div__id__endswith="google") -> /body//div[ends-with(@id, "google")]
# .filter(div__id__istartswith="google") -> /body//div[starts-with(@id, "google")]
# .filter(div__id__iendswith="google") -> /body//div[ends-with(@id, "google")]
# .filter(div__id__exact="google") -> /body//div[@id="google"]
# .filter(div__id__iexact="google") -> /body//div[(@id="google") or (@id="Google")]
# .filter(div__id__isnull=False) -> /body//div[@id=]
# .filter(div__id="fast", div__id="google") -> /body//div[(@id="fast") and (@id="Google")]
# .filter(X(div__id="google", position=2)) -> /body//div[@id="google"][position()=1]
# .filter(X(div__id="google", following_sibling="ul"))
# .filter(X(div__id="google", preceding_sibling	="ul"))
# .filter(Q(div__id="google") | Q(div__id="facebook")) -> /body//div[(@id="google") or (@id="facebook")]
# .filter(A(F("div", id="google", position=2), F("div", id="google"), output="values")) -> /body//div[@id="google" and position()=2] + /body//div[@id="google"]
# .filter(Case(Where("div__id=google", "Amazon"))) -> /body//div[@id="google"] or "Amazon"
# .aggregate(Sum(div__id="google")) -> /body//div[@id="google"]/text()
# .filter(P(Q(div__id="google"), Q("ul", first=False), Q(X("li", position=1)))) -> /body//div[@id="google"]//ul/li[position()=1]

QUERY_OPERATORS = ['eq', 'ne', 'contains', 'icontains', 'startswith', 'istartswith',
                   'endswith', 'iendswith', 'lt', 'lte', 'gt', 'gte', 'exact', 'isnull']


class Expression:
    from_root = False

    def __init__(self, bits):
        self.bits = bits
        self.conditions, self.value = bits
        # print(self.conditions)
        self.tag, self.attr, self.value = self.conditions

    def __repr__(self):
        return f'{self.__class__.__name__}(for={self.bits})'

    def get_node(self, compiler):
        node = None
        if 'startswith' in self.conditions:
            node = nodes.StringFunctions(
                self.tag,
                self.attr,
                self.value,
                function='starts-with'
            )
        elif 'endswith' in self.conditions:
            node = nodes.StringFunctions(
                self.tag,
                self.attr,
                self.value,
                function='ends-with'
            )
        elif 'eq' in self.conditions:
            node = nodes.ConditionNode(
                tag=self.tag,
                attr=self.attr,
                value=self.value,
                predicates=compiler.get_predicate(self.conditions)
            )
        node.as_xml()
        return node


class BaseExpressions:
    expression_class = Expression

    def __init__(self):
        self.bits = []

    def resolve_conditions(self, condition):
        default_operator = 'eq'
        id_value = None
        items = condition.split('__')
        if len(items) == 1:
            tag = items[-1]
        elif len(items) == 2:
            tag, id_value = items
        else:
            tag, id_value, default_operator = items
        if default_operator not in QUERY_OPERATORS:
            raise ValueError(f'Operator {default_operator} is not valid')
        return tag, id_value, default_operator

    def resolve(self, expression):
        expressions = []
        for lhv, rhv in expression.items():
            expressions.append((self.resolve_conditions(lhv), rhv))

        for expression in expressions:
            self.bits.append(self.expression_class(expression))


class Query(BaseExpressions):
    iterable_class = Iterable
    base_node = nodes.BaseNode

    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return str(self.iterable_class)

    def get_initial_nodes(self):
        self.resolve(self.expression)
        self.base_node()


e = BaseExpressions()
e.resolve({
    # 'div__id__contains': 'google',
    # 'div__id': 'facebook'
    'ul': None
})
print(e.bits)
