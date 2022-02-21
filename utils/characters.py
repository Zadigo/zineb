# from html.parser import HTMLParser
import random
from typing import Any

from zineb.utils.encoders import convert_to_unicode
from zineb.utils.iteration import drop_while

ESCAPE_CHARACTERS = ('\n', '\t', '\r')

HTML5_WHITESPACE = ' \t\n\r\x0c'

RANDOM_STRING_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def replace_escape_chars(value: str, replace_by: Any=u'', encoding: str=None):
    """
    Replaces/removes the escape characters that are often found
    in strings retrieved from the internet. They are replaced
    by default ''
    """
    text = convert_to_unicode(value)
    for escape_char in ESCAPE_CHARACTERS:
        text = text.replace(escape_char, convert_to_unicode(replace_by, encoding))
    return text


def strip_white_space(text: str):
    """
    Strips the leading and trailing white space
    from a string. This does not affect space within
    an the string e.g. Kendall\rJenner, the \\r will
    not be affected

    Parameters
    ----------

        text (str): value to correct
    """
    return text.strip(HTML5_WHITESPACE)


def deep_clean(value: str):
    """
    Special helper for cleaning words that have a
    special characters between them and for which the 
    normal `replace_escape_chars` does not modify
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


# class CustomStripper(HTMLParser):
#     def __init__(self):
#         super().__init__(convert_charrefs=False)
#         self.results = []

#     def handle_data(self, data: str):
#         self.results.append(data)
    
#     def handle_entityref(self, name: str):
#         self.results.append(f'&{name}')

#     def handle_charref(self, name: str):
#         self.results.append(f'&#{name}')

#     @property
#     def data(self):
#         return ''.join(self.results)


# def strip_html_tags(value: str):
#     instance = CustomStripper()
#     instance.feed(value)
#     instance.close()
#     result = instance.data
#     return result

# a = strip_html_tags('</adf>a')
# print(a)
