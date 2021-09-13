import re
from urllib.parse import urlparse

from zineb import global_logger


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


def url_is_secure(url: str):
    parsed_url = urlparse(url)
    return parsed_url.scheme == 'https'


def check_url_against_domain(url: str, domain: str):
    if domain.startswith('http'):
        global_logger.logger.warn(f'Domain {domain} is not valid.')
        return False
    parsed_url = urlparse(url)
    return parsed_url.netloc == domain


def replace_urls_suffix(urls: list, suffix: str, replace_with: str):
    """
    Replace the end part of each url by a string of choice
    
    Parameters
    ----------

        urls (list): lit of urls
        suffix (str): the current suffix
        replace_with (str): the suffix to implement

    Returns:
        [type]: [description]
    """
    replaced_urls = map(lambda url: str(url).removesuffix(suffix), urls)
    return list(map(lambda url: url + replace_with, replaced_urls))


def reconstruct_url(url, pattern=None, func=None):
    if pattern is not None:
        match = re.search(pattern, url)
        if match:
            return match.groups(default=None)

    if func is not None:
        return func(url)

    return None
