from w3lib.html import replace_escape_chars, strip_html5_whitespace

def deep_clean(value:str):
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
