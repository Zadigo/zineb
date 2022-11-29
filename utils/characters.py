# from html.parser import HTMLParser
import random
from typing import Any

from zineb.utils.encoders import convert_to_unicode
from zineb.utils.iteration import drop_while

ESCAPE_CHARACTERS = ('\n', '\t', '\r')

HTML5_WHITESPACE = ' \t\n\r\x0c'

RANDOM_STRING_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def replace_escape_chars(value, replace_by=u'', encoding=None):
    """
    Replaces/removes the escape characters that are often found
    in strings retrieved from the internet by replacing them
    with the default unicode ''

    >>> replace_escape_chars('Kendall\\nJenner')
    ... "Kendall Jenner"
    """
    text = convert_to_unicode(value)
    for escape_char in ESCAPE_CHARACTERS:
        text = text.replace(escape_char, convert_to_unicode(replace_by, encoding))
    return text


def strip_white_space(text):
    """
    Strips the leading and trailing white space
    from a string. Some escape characters wil not
    be affected by the stripping e.g. Kendall\rJenner

    >>> strip_white_space('Kendall\\rJenner')
    ... "Kendall Jenner"
    """
    return text.strip(HTML5_WHITESPACE)


def deep_clean(value: str):
    """
    Special helper for cleaning words that have
    special and for which the normal `replace_escape_chars` 
    does not modify

    >>> deep_clean('Kendall\\nJenner\\r)
    ... "Kendall Jenner"
    """
    value = replace_escape_chars(strip_white_space(value), replace_by=' ')
    cleaned_words = drop_while(lambda x: x == '', value.split(' '))
    return ' '.join(cleaned_words)


def create_random_string(length: int=5, lowercased: bool=False):
    """Return a random string"""
    result = ''.join(random.choice(RANDOM_STRING_CHARS) for _ in range(length))
    if lowercased:
        return result.lower()
    return lowercased
