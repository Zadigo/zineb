import re

CLOSING_TAGS = {
    'html', 'body', 'main', 'article', 'div', 'span',
    'script', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'p',
    'title', 'a', 'button', 'aside', 'strong', 'var', 'u',
    'ul', 'li', 'table', 'th', 'td', 'tr', 'thead', 'tfoot',
    'tbody', 'section', 'i', 'q', 'nav', 'form', 'label',
    'small', 'svg', 'time', 'video', 'u', 'figure', 'figcaption',
    'fieldset', 'em', 'dl', 'dt', 'dd', 'dialog', 'datalist',
    'colgroup', 'caption'
}

SELF_CLOSING_TAGS = {
    'meta', 'link', 'audio', 'video', 'area', 'base',
    'embed', 'br', 'hr', 'input', 'img', 'spacer', 'frame'
}

NON_CLOSED_TAGS = {
    'br', 'input', 'img', 'source', 'track', 'option', 'col'
}


def is_newline(value: str):
    if value == '':
        return False
    if '\n' in value:
        return True
    return False


def is_empty(value: str):
    return value == ''


def requires_closing(name: str):
    """Tags that require a closing tag"""
    return name in CLOSING_TAGS


def requires_self_close(name: str):
    return name in SELF_CLOSING_TAGS
