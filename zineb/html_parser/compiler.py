from lxml import etree
from zineb.html_parser.nodes import WhereNode


class BaseCompiler:
    encoding = 'utf-8'
    html_compiler = etree.HTMLParser
    where_node = WhereNode

    def __init__(self, content):
        self.content = etree.fromstring(
            content,
            self.html_compiler(encoding=self.encoding)
        )

    def build_queryset(self):
        pass


class XMLCompiler(BaseCompiler):
    pass


with open('tests/html/form.html', mode='r') as f:
    x = XMLCompiler(f.read())
    print(x)
