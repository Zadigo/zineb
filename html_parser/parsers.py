from collections import Counter, deque
from functools import cached_property
from html.parser import HTMLParser
from io import StringIO
from typing import Union

from zineb.html_parser.html_tags import Comment, ElementData, NewLine, Tag
from zineb.html_parser.managers import Manager
from zineb.html_parser.utils import break_when
from zineb.utils.iteration import keep_while


class Algorithm(HTMLParser):
    """Subclasses html.HTMlParser in order to
    process the html tags. This should not be
    subclassed or used directly"""
    
    def __init__(self, extractor, **kwargs):
        self.extractor = extractor
        self.index = 0
        super().__init__(**kwargs)
    
    @property
    def _increase_index(self):
        self.index = self.index + 1
        return self.index

    def handle_startendtag(self, tag, attrs):
        self.extractor.self_closing_tag(tag, attrs, position=self.getpos())

    def handle_starttag(self, tag, attrs):
        self.extractor.start_tag(tag, attrs, position=self.getpos(), index=self._increase_index)

    def handle_endtag(self, tag):
        self.extractor.end_tag(tag)

    def handle_data(self, data):
        self.extractor.internal_data(data, position=self.getpos(), index=self._increase_index)
        
    def handle_comment(self, data):
        self.extractor.parse_comment(data, position=self.getpos())


class Extractor:
    """The main interface that deals with processing
    each tag sent by the Algorithm"""
    
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

        # Iterate over the container
        # in order to find tags that are not
        # closed. Using this technique, we will
        # then know that these tags are the parents
        # of the current tag by definition
        
        unclosed_tags = list(keep_while(lambda x: not x.closed, self.container))
        # print(tag, unclosed_tags)

        klass = Tag(tag, attrs, extractor=self)
        self.container.append(klass)
        self._current_tag = klass

        klass._parents = unclosed_tags

        # Add the newly created tag to
        # the children list of the
        # all the previous tags
        self.recursively_add_tag(klass)

        v_position, h_position = kwargs.get('position', (None, None))
        klass.vertical_position = v_position
        klass.horizontal_position = h_position
        self._coordinates.append((v_position, h_position))
        klass.index = kwargs.get('index')
        
        # print(tag, kwargs.get('position'))
        # print(kwargs)
        # print(tag)

    def end_tag(self, tag):
        def filter_function(x):
            return x == tag and not x.closed
        
        tag_to_close = break_when(filter_function, self.container)
        tag_to_close.closed = True
        # print('/', tag, tag_to_close)

    def internal_data(self, data, **kwargs):
        data_instance = None
        # \n is sometimes considered as
        # data witthin a tag we need to 
        # deal with strings that
        # come as "\n   " and represent
        # them as NewLine if necessary
        if '\n' in data:
            element = data.strip(' ')
            if element == '\n':
                data_instance = NewLine(extractor=self)
            else:
                data_instance = ElementData(element, extractor=self)
        else:
            data_instance = ElementData(data, extractor=self)
            
        x, y = kwargs.get('position', (None, None))
        data_instance.vertical_position = x
        data_instance.horizontal_position = y
        # print('>', data_instance, kwargs.get('position'))
        data_instance.index = kwargs.get('index')

        try:
            # Certain tags do not have an internal_data
            # attribute and will raise an error because 
            # technically they are not supposed to contain
            # data. In that specific case, if the current tag
            # is a data element, just skip on error
            self._current_tag._internal_data.append(data_instance)
        except:
            pass
        
        
        self.recursively_add_tag(data_instance)
        self.container.append(data_instance)
        # print(data)

    def self_closing_tag(self, tag, attrs, **kwargs):
        """Handle tags that are self closed example <link>, <img>"""
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
    """The main class used to process the html page.
    It implements the default manager for querying
    the different items on the html page"""
    
    def __init__(self, html: Union[str, StringIO]=None):
        self.manager = Manager(self)
        super().__init__()

        # if html is not None:
        #     html_string = html
        #     if isinstance(html, StringIO):
        #         html_string = html.read()
        #     self.resolve(html_string)