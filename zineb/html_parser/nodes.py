from lxml import etree


class Node:
    representation = None
    is_function_node = False
    is_definitive = True

    def __init__(self, tag=None, attribute=None, value=None):
        self.tag = tag
        self.attribute = attribute
        self.value = value
        self.result = None

    def __repr__(self):
        return f'<{self.__class__.__name__}[{self.representation}]>'

    def __str__(self):
        return self.result

    def get_representation(self):
        return self.representation

    def as_xml(self):
        self.result = self.representation

    def finalize_node(self):
        return [self.representation]


class BaseNode(Node):
    representation = '/body'



class Tag(Node):
    representation = '{tag}'

    def __init__(self, predicates=None, **kwargs):
        super().__init__(**kwargs)
        self.predicates = predicates

    def as_xml(self):
        if self.predicates is not None:
            self.representation = '{tag}[{predicates}]'


class Child(Node):
    representation = '/{tag}'

    def as_xml(self):
        self.result = self.representation.format(tag=self.tag)


class Descendent(Child):
    representation = '//{tag}'


class NodeFunctions(Node):
    representation = '{function}()'
    is_function_node = True
    NAME = 'name'
    TEXT = 'text'
    COUNT = 'count'
    POSITION = 'position'


class StringFunctions(Node):
    representation = '{function}(@{attribute}, {value})'
    is_function_node = True
    CONTAINS = 'contains'
    STARTS_WITH = 'starts-with'
    ENDS_WITH = 'ends-with'
    CONCAT = 'concat'
    SUBSTRING = 'substring'
    TRANSLATE = 'translate'
    NORMALIZE_SPACE = 'normalize-space'
    STRING_LENGTH = 'string-length'

    def __init__(self, tag=None, value=None, attribute=None, function='contains'):
        super().__init__(tag, attribute)
        self.function = function
        self.value = value

    def as_xml(self):
        self.result = self.representation.format(
            function=self.function,
            attribute=self.attribute,
            value=self.value
        )


class ConditionNode(Node):
    representation = '{lhv}{operation}{rhv}'

    def as_xml(self):
        if self.is_definitive:
            result = self.representation.format(
                lhv=self.tag,
                operation='=',
                value=self.value
            )
            self.result = f'[{result}]'
        else:
            pass


class Operators(Node):
    representation = '{lhv} {operator} {rhv}'
    complexe_comparision = False
    AND = 'and'
    OR = 'or'

    def __init__(self, operator='and'):
        self.operator = operator
        super().__init__()

    def as_xml(self):
        super().build_node()
        if self.complexe_comparision:
            # ex. //div[(x and y) or not(z)]
            self.result = f'({self.representation})'


class WhereNode(Node):
    operators = Operators

    def __init__(self, if_node, then_node, default_node=None, **kwargs):
        super().__init__(**kwargs)
        self.if_node = if_node
        self.then_node = then_node
        self.default_node = default_node

    def as_xml(self):
        self.operators()


s = StringFunctions(tag='div', value='Kendall', attribute='id')
s.build_node()
print(s)


# with open('tests/html/form.html', mode='r') as f:
#     content = f.read()
#     x = etree.fromstring(content, etree.HTMLParser(encoding='utf-8'))
#     d = DocumentTitle()
#     d.build_node()
#     # print(x.find('body//form//button[contains(text(), "Submit")]'))
#     y = etree.XPath('body//form//button[contains(text(), "Submit")]')
#     w = y(x)
#     print(w[0].text)
