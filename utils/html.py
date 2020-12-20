from w3lib.html import strip_html5_whitespace

def deep_clean(value:str):
    """
    Special helper for cleaning words that have a
    spaces and "\\n" values between them

    Args:
        value ([type]): [description]

    Returns:
        generator: [description]
    """
    value = strip_html5_whitespace(value)
    if '\n' in value:
        value = value.replace('\n', '')
    tokens = value.split(' ')
    cleaned_words = filter(lambda x: x != '', tokens)
    return ' '.join(cleaned_words).strip()
