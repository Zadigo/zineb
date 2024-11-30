from lxml import etree

from zineb.html_parser.nodes import WhereNode
from zineb.utils.characters import deep_clean

class Value:
    """Represents an HTML page value"""
    def __init__(self, element):
        self.text = deep_clean(element.text)
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.text})'

    def __str__(self):
        return self.text


class BaseCompiler:
    encoding = 'utf-8'
    html_compiler_class = etree.HTMLParser

    def __init__(self, query):
        self.query = query
        self.content = query.content
        # Run multiple queries at once on
        # the current document
        self.html_compiler = None
        self.complex_nodes = []

    def get_predicate(self, value):
        if 'eq' in value or 'contains' in value:
            return '@{value[-0]}={value[-1]}'

    def get_nodes(self):
        nodes = []
        for expression in self.query.bits:
            self.nodes.append(expression.get_node(self))
        return ''.join(nodes)

    def get_xpath_compiler(self):
        instance = etree.XPath(self.get_nodes())
        return instance

    def get_base_compiler(self):
        compiler = self.html_compiler_class(
            encoding=self.encoding,
            remove_comments=True,
            remove_blank_text=True
        )
        return etree.fromstring(self.content, compiler)

    def compile(self):
        xpath_compiler = self.get_xpath_compiler()
        result = xpath_compiler(self.get_base_compiler())
        if isinstance(result, list):
            for item in result:
                value = Value(item)
        else:
            pass
