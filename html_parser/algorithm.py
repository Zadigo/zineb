from html.parser import HTMLParser
from typing import Callable, DefaultDict, OrderedDict

class CustomHTMLParser(HTMLParser):
    """This custom HTMLParser uses the builtin HTMLParser
    to parse the HTML document and then defer the actual
    handling the parsed data to the BaseBuilder"""
    def __init__(self, builder: Callable):
        super().__init__(convert_charrefs=False)
        self.builder_instance = builder

    def _transform_attrs(self, attrs):
        # Rebuild attrs to look like
        # {'id': [1, 2, 3]}
        rebuilt_attrs = DefaultDict(list)
        for key, values in attrs:
            rebuilt_attrs[key].extend(values.split(' '))
        return rebuilt_attrs

    def handle_data(self, data: str):
        self.builder_instance.handle_inner_data(data)

    def handle_charref(self, name: str):
        pass

    def handle_starttag(self, tag: str, attrs: list):
        rebuilt_attrs = self._transform_attrs(attrs)
        self.builder_instance.handle_start_tag(tag, dict(rebuilt_attrs), line_position=self.getpos())

    def handle_endtag(self, tag: str):
        # print(tag)
        self.builder_instance.handle_end_tag(tag)

    def handle_startendtag(self, tag: str, attrs: list):
        # print(tag, attrs)
        rebuilt_attrs = self._transform_attrs(attrs)
        self.builder_instance.handle_self_closing_tag(tag, rebuilt_attrs)

    def handle_entityref(self, name: str):
        # print(name)
        pass

    def handle_comment(self, data: str):
        self.builder_instance.handle_comment(data)


# custom = CustomParser()
# custom.feed(HTML)
# custom.close()
