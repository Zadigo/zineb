from ctypes import Union

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
    'meta', 'video', 'img'
}


def filter_by_name(data, name: str):
    """Filter tags by name"""
    for item in data:
        if item.name == name:
            yield item


def filter_by_attrs(data, attrs: dict={}):
    """Filter tags by attributes"""
    for attr, value in attrs.items():
        for item in data:
            result = item.get_attr(attr)
            if result == value:
                yield item


def filter_by_name_or_attrs(data, name, attrs={}):
    """Filter by name or attributes"""
    tags_by_name = filter(lambda x: x.name == name, data)

    def attrs_filtering_option(x):
        if attrs:
            for attr, value in attrs.items():
                result = x.get_attr(attr)
                if result == value:
                    return x
        else:
            return x
    return (attrs_filtering_option(x) for x in tags_by_name)


def break_when(func, items):
    """Iterate over a list of items and
    breaks on the first match"""
    for item in items:
        if func(item):
            break
    return item
