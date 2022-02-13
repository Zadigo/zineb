import re
from typing import Callable
from urllib.parse import urlparse

from zineb.logger import global_logger

URL_REGEX = r'^(file|https?)\:\/{2}(?:.*)$'

def is_url_regex_check(url: str):
    """
    "http://" alone is considered a url when it is not a valid one
    by is_url, this function ensures that there is actual netloc
    that follows
    """
    result = re.match(URL_REGEX, url)
    if result:
        return True
    return False


def is_url(url: str):
    return url.partition('://')[0] in ('http', 'https', 'file')


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

        - urls (list): lit of urls
        - suffix (str): the current suffix
        - replace_with (str): the suffix to implement

    Returns:
        [type]: [description]
    """
    def factory(url):
        url = str(url).removesuffix(suffix)
        url = url + replace_with
        return url
    return list(map(factory, urls))


# def reconstruct_url(url: str, pattern: str=None, func: Callable=None):
#     if pattern is not None:
#         matched = re.match(pattern, url)
#         if matched:
#             return matched.groups()

#     if func is not None:
#         return func(url)

#     return None
