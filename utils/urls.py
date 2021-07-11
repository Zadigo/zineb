import re

URL_REGEX = r'^https?\:\/\/.*$'

def is_url_regex_check(url: str):
    """
    The is_url() from w3lib only checks for the existence
    of "://" within the string to determine if it's a url.

    However, just "http://" is considered a url when it is not so,
    this extra check makes sure that the url follows the very

    Args:
        url (str): [description]
    """
    result = re.match(URL_REGEX, url)
    if result:
        return True
    return False
