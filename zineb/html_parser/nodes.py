class Node:
    representation = None
    is_function_node = False

    def __init__(self, tag=None, attribute=None, value=None):
        self.tag = tag
        self.attribute = attribute
        self.value = value
        self.result = None

    def __repr__(self):
        return f'<{self.__class__.__name__}[{self.representation}]>'

    def __str__(self):
        return self.result or '<Empty Node>'

    def build_node(self):
        pass


class Child(Node):
    representation = '/{tag}'

    def build_node(self):
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

    def __init__(self, tag=None, attribute=None, function='contains'):
        super().__init__(tag, attribute)
        self.function = function


class WhereNode(Node):
    pass


s = Child(tag='div')
s.build_node()
print(s)
