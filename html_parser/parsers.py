from collections import Counter, deque
from functools import cached_property
from html.parser import HTMLParser
from io import StringIO
from typing import Union

from zineb.html_parser.html_tags import Comment, ElementData, NewLine, Tag
from zineb.html_parser.managers import Manager
from zineb.html_parser.utils import break_when


class Algorithm(HTMLParser):
    def __init__(self, extractor, **kwargs):
        self.extractor = extractor
        super().__init__(**kwargs)

    def handle_startendtag(self, tag, attrs):
        self.extractor.self_closing_tag(tag, attrs, position=self.getpos())

    def handle_starttag(self, tag, attrs):
        self.extractor.start_tag(tag, attrs, position=self.getpos())

    def handle_endtag(self, tag):
        self.extractor.end_tag(tag)

    def handle_data(self, data):
        self.extractor.internal_data(data)
        
    def handle_comment(self, data):
        self.extractor.parse_comment(data, position=self.getpos())


class Extractor:
    HTML_PAGE = None

    def __init__(self):
        self.algorithm = Algorithm(self)
        self._opened_tags = Counter()

        self._current_tag = None

        # Contains the collected tags
        # and represents the HTML tree
        self.container = deque()
        
        # Stores all the positions of
        # the items that were parsed
        self._coordinates = []

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self.container)})"

    def __getitem__(self, index):
        return self.container[index]
    
    def __iter__(self):
        return iter(self.container)
    
    # def __contains__(self, value):
    #     print(value)
    #     return value in self.container
    
    def __len__(self):
        return len(self.container)

    def __enter__(self, **kwargs):
        return self.container

    def __exit__(self, *args, **kwargs):
        return False

    @cached_property
    def get_container(self):
        return self.container

    @property
    def get_previous_tag(self):
        try:
            return self.container[-2]
        except IndexError:
            # There is not previous so
            # just return None
            return None
        
    def _get_default_prettifier(self, html: str) -> str:
        """Function that normalizes the incoming
        html string so that we can deal with a
        standard format"""
        from lxml.etree import tostring
        from lxml.html import fromstring
        
        return tostring(fromstring(html), encoding='unicode', pretty_print=True)

    def recursively_add_tag(self, instance):
        """Adds the current tag recursively 
        to all the previous tags that are open"""
        for i in range(0, len(self.container) - 1):
            tag = self.container[i]
            if not tag.closed:
                tag._children.append(instance)

    def resolve(self, html: str):
        """Entrypoint for transforming each html 
        string tags into Python objects"""
        
        self.HTML_PAGE = self._get_default_prettifier(html)
        # self.HTML_PAGE = html
        self.algorithm.feed(self.HTML_PAGE)
        self.algorithm.close()

    def start_tag(self, tag, attrs, **kwargs):
        self._opened_tags.update([tag])

        klass = Tag(tag, attrs, extractor=self)
        self.container.append(klass)
        self._current_tag = klass

        # Iterate over the container
        # in order to find tags that are not
        # closed. Using this technique, we will
        # then know that these tags are the parents
        # of the current tag. Also, the first iteration
        # will be the parent of the tag.
        # unclosed_tags = list(filter(lambda x: not x.closed, self.container))
        # klass.parents = unclosed_tags
        # try:
        #     klass.parent = unclosed_tags[-2]
        # except:
        #     klass.parent = unclosed_tags[-1]

        # Add the newly created tag to
        # the children list of the
        # all the previous tags
        self.recursively_add_tag(klass)

        v_position, h_position = kwargs.get('position', (None, None))
        klass.vertical_position = v_position
        klass.horizontal_position = h_position
        self._coordinates.append((v_position, h_position))
        
        # print(kwargs.get('position'))
        # print(kwargs)
        # print(tag)

    def end_tag(self, tag):
        def filter_function(x):
            # return x == tag and not self._current_tag.closed
            return x == tag and not x.closed
        # TODO: Function sometimes returns the wrong
        # tag that needs to be closed
        tag_to_close = break_when(filter_function, self.container)
        tag_to_close.closed = True
        # print('/', tag, tag_to_close)

    def internal_data(self, data):
        data_instance = ElementData(data)
        try:
            self._current_tag._internal_data.append(data_instance)
        except:
            # print("Does not have current")
            pass
        else:
            self.recursively_add_tag(data_instance)
            self.container.append(data_instance)
        # print(data)

    def self_closing_tag(self, tag, attrs, **kwargs):
        """Handle tags that are self closed example <link />"""
        self._opened_tags.update([tag])

        klass = Tag(tag, attrs, extractor=self)
        self.container.append(klass)
        self._current_tag = klass
        klass.closed = True

        self.recursively_add_tag(klass)

        v_position, h_position = kwargs.get('position')
        klass.vertical_position = v_position
        klass.horizontal_position = h_position
        
    def parse_comment(self, data: str, **kwargs):
        klass = Comment(data)
        self.container.append(klass)
        self._current_tag = klass
        klass.closed = True
        
        self.recursively_add_tag(klass)
        
        v_position, h_position = kwargs.get('position')
        klass.vertical_position = v_position
        klass.horizontal_position = h_position


class General(Extractor):
    def __init__(self, html: Union[str, StringIO] = None):
        self.manager = Manager(self)
        super().__init__()

        # if html is not None:
        #     html_string = html
        #     if isinstance(html, StringIO):
        #         html_string = html.read()
        #     self.resolve(html_string)
