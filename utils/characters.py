from typing import Any

from zineb.utils.encoders import convert_to_unicode
from zineb.utils.iteration import drop_while


ESCAPE_CHARACTERS = ('\n', '\t', '\r')

HTML5_WHITESPACE = ' \t\n\r\x0c'


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
    from a sting 

    Parameters
    ----------

        text (str): value to correct
    """
    return text.strip(HTML5_WHITESPACE)


def deep_clean(value: str):
    """
    Special helper for cleaning words that have a
    spaces values between them and for which the 
    normal `replace_escape_chars` does not modify

    Parameters
    ----------

        value (str): value to clean

    Returns
    -------

        str: words in clean form
    """
    value = replace_escape_chars(strip_white_space(value))
    cleaned_words = drop_while(lambda x: x == '', value.split(' '))
    return ' '.join(cleaned_words).strip()
