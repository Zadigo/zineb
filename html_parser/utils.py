HTML_TAGS = {
    'html', 'body', 'main', 'p', 'a', 'br', 'table', 'td', 'tr',
    'th', 'b', 'i', 'script'
}

SELF_CLOSING_TAGS = {
    'link', 'br'
}


def filter_by_name_or_attrs(data, name, attrs={}):
    """External helper function that is used to filter
    over a queryset data by name or by
    certain attrs"""
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
    item = None
    for item in items:
        if func(item):
            break
    return item
