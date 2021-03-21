import re

from w3lib.html import replace_escape_chars, strip_html5_whitespace


def deep_clean(value: str):
    """
    Special helper for cleaning words that have a
    spaces and "\\n" values between them

    Parameters
    ----------

        value (str): value to clean

    Returns
    -------

        str: words in clean form
    """
    value = replace_escape_chars(
        strip_html5_whitespace(value), replace_by=''
    )
    cleaned_words = filter(lambda x: x != '', value.split(' '))
    return ' '.join(cleaned_words).strip()


def is_path(path):
    is_match = re.search(r'^(?:[/].*/)(?:.*)$', path)
    if is_match:
        return True
    return False


def decode_email(value):
    """
    Decodes a protected email from an HTML
    response. Generally, this is a x bits
    length string under `data-cfemail` that
    some websites put in place prevent
    people from scrapping the emails

    Args:
        value ([type]): [description]

    Returns:
        [type]: [description]
    """
    de = ''
    k = int(value[:2], 16)

    for i in range(2, len(value)-1, 2):
        de += chr(int(value[i:i+2], 16) ^ k)

    return de
