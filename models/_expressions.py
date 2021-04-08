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
        self.__init__(html_document=html_document,
                      html_tag=html_tag, response=response)

    @staticmethod
    def _expression_resolver(expression):
        try:
            tag_name, pseudo = expression.split('__', 1)
        except:
            # If no pseudo is passed, just use the default
            # text one by appending it to the expression
            expression = expression + '__text'
            tag_name, pseudo = expression.split('__', 1)

        matched_elements = re.search(
            r'(?P<tag>\w+)(?P<marker>\.|\#)?(?P<attr>\w+)?', tag_name)
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

    def parse(self, expression, many=True):
        tag_name, pseudo, attrs = self._expression_resolver(expression)
        if many:
            tags = self.parser.find_all(tag_name, attrs=attrs)
            results = [self._resolve_pseudo(pseudo, tag) for tag in tags]
        else:
            tag = self.parser.find(tag_name, attrs=attrs)
            results = [self._resolve_pseudo(pseudo, tag)]
        return results
