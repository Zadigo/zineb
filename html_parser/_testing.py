from collections import Counter, deque
from functools import cached_property
from html.parser import HTMLParser
from io import StringIO
from turtle import position
from typing import Callable, List, OrderedDict, Union

from zineb.utils.characters import deep_clean
from zineb.utils.iteration import keep_while

HTML_TAGS = {
    'html', 'body', 'main', 'p', 'a', 'br'
}

SELF_CLOSING_TAGS = {
    'link', 'br'
}


class QuerySet:
    def __init__(self):
        self._data = []

    def __repr__(self):
        return f"{self.__class__.__name__}({self._data})"

    def __iter__(self):
        return next(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    @classmethod
    def copy(cls, data):
        instance = cls()
        instance._data = list(data)
        return instance

    @property
    def first(self):
        return self._data[0]

    @property
    def last(self):
        return self._data[-1]


def break_when(func, items):
    item = None
    for item in items:
        if func(item):
            break
    return item


class QueryMixin:
    @property
    def _has_extractor(self):
        return self._extractor_instance is not None

    @property
    def previous_element(self):
        """Return the element directly before this tag"""
        pass

    @property
    def next_element(self):
        """Return the element directly next to this tag"""
        position_of_next = self.vertical_position + 1
        for item in self._extractor_instance.get_container:
            if item.vertical_position == position_of_next:
                break
        return item

    def get_attr(self, name: str) -> Union[str, None]:
        return self.attrs.get(name, None)

    def get_previous(self, name: str):
        with self._extractor_instance as items:
            pass

    def get_next(self, name: str):
        with self._extractor_instance as items:
            pass

    def get_all_previous(self, name: str):
        if not self._has_extractor:
            raise TypeError('To use to query with tags, need an extractor')
            # return []

        def filtering_function():
            with self._extractor_instance as items:
                for item in items:
                    if (item.vertical_position < self.vertical_position and
                            item.name == name):
                        yield item

        return QuerySet.copy(filtering_function())

    def get_all_next(self, name: str):
        if not self._has_extractor:
            raise TypeError('To use to query with tags, need an extractor')

        def filtering_function():
            with self._extractor_instance as items:
                for item in items:
                    if (item.vertical_position > self.vertical_position and
                            item.name == name):
                        yield item

        return QuerySet.copy(filtering_function())

    def children(self, **expression):
        pass


class BaseTag(QueryMixin):
    def __init__(self, name: str, attrs: dict = {}, extractor: Callable = None):
        self.name = name
        self.attrs = self._build_attrs(attrs)

        self.closed = False
        self._internal_data = deque()
        self._children = deque()

        # self.next_element = None
        # self.previous_element = None

        self.vertical_position = 0
        self.horizontal_position = 0

        # An instance of the class that extracts
        # in order to be able to access other
        # items in the HTML tree
        # if not isinstance(extractor, Extractor):
        #     raise TypeError('Extractor should be an instance of Extractor')
        self._extractor_instance = extractor

        # self.parents = deque()
        # self.parent = None

    def __repr__(self):
        if self.attrs:
            return f'<{self.name} {self._attrs_to_string}>'
        return f'<{self.name}>'

    # def __str__(self):
    #     return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, value):
        return value == self.name

    def __getitem__(self, value):
        return self.attrs.get(value, None)

    @property
    def children(self):
        # return self._children
        return QuerySet.copy(self._children)

    @property
    def string(self) -> Union[str, None]:
        # When we have one item, return it,
        # otherwise, with multiple data elements
        # we cannot tell which element to refer
        # to then we should just return None
        if len(self._internal_data) == 1:
            return self._internal_data[0]
        return None

    @property
    def clean_string(self):
        return deep_clean(self.string)

    @staticmethod
    def _build_attrs(attrs):
        attrs_dict = OrderedDict()
        for key, value in attrs:
            attrs_dict.setdefault(key, value)
        return attrs_dict

    @property
    def _attrs_to_string(self):
        items = []
        for key, value in self.attrs.items():
            items.append(f'{key}="{value}"')
        return ''.join(items)

    def has_attr(self, name: str):
        return name in self.attrs.keys()


class Tag(BaseTag):
    pass


class StringMixin(QueryMixin):
    def __init__(self, data):
        self.name = None
        self.data = data
        self.closed = True

        self.horizontal_position = 0
        self.vertical_position = 0

        self.parents = []
        self.parent = None

    def __repr__(self):
        return self.data

    def __eq__(self, value):
        return self.data == value

    def __contains__(self, value):
        return value in self.data

    @property
    def string(self):
        return self.data

    def has_attr(self):
        return False

    def get_attr(self, name: str):
        return None


class NewLine(StringMixin):
    def __init__(self):
        super().__init__('\n')


class ElementData(StringMixin):
    def __init__(self, data):
        super().__init__(data)
        self.name = 'data'


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


class Extractor:
    HTML_PAGE = None

    def __init__(self):
        self.algorithm = Algorithm(self)
        self._opened_tags = Counter()

        self._current_tag = None
        # self._immediately_parsed_element = None

        # Contains the collected tags
        # and represents the HTML tree
        self.container = deque()

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self.container)})"

    def __getitem__(self, index):
        return self.container[index]

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

    def recursively_add_tag(self, instance):
        """Adds the current tag recursively 
        to all the previous tags"""
        for i in range(0, len(self.container) - 1):
            tag = self.container[i]
            if not tag.closed:
                tag._children.append(instance)

    def resolve(self, html: str):
        self.HTML_PAGE = html
        self.algorithm.feed(html)
        self.algorithm.close()

        # Create relationships
        # container = self.get_container
        # for i in range(len(container)):
        #     tag = container[i]
        #     if i > 0:
        #         try:
        #             # When we've reached the limit of the
        #             # array this raises and error that
        #             # we'll just skip
        #             tag.next_element = container[i + 1]
        #         except IndexError:
        #             pass
        #         tag.previous_element = container[i - 1]
        #     else:
        #         tag.next_element = container[i + 1]

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

        v_position, h_position = kwargs.get('position')
        klass.vertical_position = v_position
        klass.horizontal_position = h_position

        # print(kwargs)
        # print(tag)

    def end_tag(self, tag):
        def filter_function(x):
            return x == tag and not self._current_tag.closed
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


class Manager:
    def __init__(self, instance):
        self.instance = instance

    def __getattr__(self, value):
        if value in HTML_TAGS:
            return self.find(value)
        return value

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @cached_property
    def get_title(self):
        title = None
        with self.instance as items:
            for item in items:
                if item.name == 'title':
                    title = item.string
                    break
        return title

    def find(self, name: str, attrs: dict = {}) -> Tag:
        """Returns the first found element"""
        tag_to_return = None
        for tag in self.instance.get_container:
            if tag == name:
                if attrs:
                    for attr, value in attrs.items():
                        result = tag.get_attr(attr)
                        if result is not None:
                            if result == value and tag == name:
                                tag_to_return = tag
                else:
                    tag_to_return = tag
                    break
            # if attrs:
            #     for attr, value in attrs.items():
            #         result = tag.get_attr(attr)
            #         if result is not None:
            #             if result == value and tag == name:
            #                 break
            # else:
            #     if tag == name:
            #         break
        return tag_to_return

    def find_all(self, name_or_names: Union[str, list], attrs: dict = None):
        """Finds all the elements"""
        def filtering_function(tag):
            if isinstance(name_or_names, list):
                return tag.name in name_or_names
            return tag == name_or_names

        queryset = keep_while(filtering_function, self.instance.get_container)
        return QuerySet.copy(queryset)


class HTMLSoup(Extractor):
    def __init__(self, html: Union[str, StringIO] = None):
        self.manager = Manager(self)
        super().__init__()

        # if html is not None:
        #     html_string = html
        #     if isinstance(html, StringIO):
        #         html_string = html.read()
        #     self.resolve(html_string)


# s = """
# <html>
#     <body>
#         <a id="test">Question</a>
#         <a href="http://example.com">
#             <span>Height</span>
#             <span>173cm</span>
#         </a>
#         <a class="google">Test</a>
#     </body>
# </html>
# """

# s = """<html><span>Amazing</span><span>Amazing2</span></html>"""

# s = """
# <html>
# <head>
# <title>Page title</title>
# <link href="http://example.com" />
# </head>
# <body>
# Some text
# </body>
# </html>
# """
# s = """<html><head><link href="http://example.com"/></head></html>"""
s = """<html><head><title>Something</title></head></html>"""

g = HTMLSoup()
g.resolve(s)
# q = g.manager.find_all('a')
# q = g.manager.find('a', attrs={'class': 'google'})
# print(q['class'])
# print(g.manager.head.children)
