from typing import Callable, Iterator, Union, Generator

HTML_TAGS = {
    'html', 'body', 'main', 'p', 'a', 'br', 'table', 'td', 'tr',
    'th', 'b', 'i', 'script', 'span', 'abbr', 'address', 'area',
    'article', 'aside', 'audio', 'base', 'ul', 'li', 'blockquote',
    'button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup',
    'data', 'datalist', 'dd', 'dl', 'dt', 'del', 'details', 'summary',
    'dialog', 'div', 'embed', 'fieldset', 'legend', 'input', 'label',
    'form', 'footer', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr',
    'mark', 'meta', 'meter', 'nav', 'noscript', 'object', 'ol', 'optgroup',
    'option', 'select', 'param', 'picture', 'pre', 'progress', 'q', 'ruby',
    'section', 'small', 'source', 'span', 'style', 'sub', 'svg', 'template',
    'title', 'tfoot', 'u', 'var', 'video', 'time', 'img', 'iframe'
}


SELF_CLOSING_TAGS = {
    'link', 'br', 'base', 'embed', 'input', 'hr',
    'meta', 'video', 'img', 'area', 'br', 'col',
    'param', 'source', 'track', 'wbr'
}


def filter_by_names(items, names):
    """Filter using multiple tag names"""
    if names:
        for item in items:
            if item.name in names:
                yield item
    else:
        for item in items:
            yield item


def filter_by_name(items, name):
    """Filter by name"""
    for item in items:
        if item.name == name:
            yield item


def filter_by_attrs(items, attrs):
    """Filter by attributes"""
    # Even though attrs is required,
    # it can come as an empty dict
    # especially for tags that do
    # not have attributes. This
    # causes the iteration function
    # to be skipped and return []
    # giving the impression that
    # no tags exists especially when 
    # used in combination with filter_by_name
    if attrs:
        for attr, value in attrs.items():
            for item in items:
                result = item.get_attr(attr)
                if result == value:
                    yield item
    else:
        for item in items:
            yield item

def filter_by_name_or_attrs(data, name, attrs):
    """Filter by name and attributes"""
    tags_by_name = filter_by_name(data, name)
    return filter_by_attrs(tags_by_name, attrs)


def break_when(func: Callable, items: Union[Iterator, Generator]):
    """
    A function that immediately breaks
    when an element is matched for 
    optimization
    """
    for item in items:
        if func(item):
            break
    return item
