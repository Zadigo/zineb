import hashlib
import hmac
import re
import os
import secrets
from functools import lru_cache
from typing import Callable, Iterable
from urllib.parse import urlparse
from zineb import exceptions
from zineb.settings import settings

from zineb import global_logger


def create_new_name(length=5):
    return secrets.token_hex(nbytes=length)


def reconstruct_url(url, pattern=None, func=None):
    if pattern is not None:
        match = re.search(pattern, url)
        if match:
            return match.groups(default=None)
    
    if func is not None:
        return func(url)

    return None


def replace_urls_suffix(urls:list, suffix: str, replace_with: str):
    """
    Replace the end part of each url by a string
    
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
    

def create_secret_key(salt, encoding='utf-8', errors='strict'):
    salt = str(salt).encode(encoding, errors)
    result = str('something').encode(encoding, errors)
    hash_value = hashlib.md5(salt + result).digest()
    hmac_result = hmac.new(hash_value, 'Some message'.encode(encoding, errors), hashlib.sha256)
    return hmac_result.hexdigest()


ALLOWED_CHARACTERS = (
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)

def random_string(length=15):
    return ''.join(secrets.choice(ALLOWED_CHARACTERS) for _ in range(length))


def url_is_secure(url:str):
    parsed_url = urlparse(url)
    return parsed_url.scheme == 'https'


def check_url_against_domain(url:str, domain:str):
    if domain.startswith('http'):
        global_logger.logger.warn(f'Domain {domain} is not valid.')
        return False
    parsed_url = urlparse(url)
    return parsed_url.netloc == domain


def keep_while(func: Callable, values: Iterable):
    for value in values:
        result = func(value)
        if result:
            yield value


def drop_while(func: Callable, values: Iterable):
    for value in values:
        result = func(value)
        if not result:
            yield value


def split_while(func: Callable, values: Iterable):
    a = [value for value in values if func(value)]
    b = [value for value in values if not func(value)]
    return a, b


def transform_to_bytes(content: str):
    """
    Transform a string to bytes

    Parameters
    ----------

        - content (str): The string to convert

    Raises
    ------

        ValueError: the string is not valid

    Returns
    -------

        - bytes: the converted string in bytes
    """
    if isinstance(content, bytes):
        return content

    if isinstance(content, str):
        return content.encode(encoding='utf-8')
    else:
        raise ValueError(("In order to transform the object to bytes "
        "you need to provide a string."))


@lru_cache(maxsize=0)
def collect_files(path: str, func: Callable=None):
    """
    Collect all the files within specific
    directory of your project. This utility function
    is very useful with the FileCrawler:

        class Spider(FileCrawler):
            start_files = collect_files('some/path')

    Parameters
    ----------

        - path (str): relative path to the directory
        - func (Callable): a callback function to use on the files 

    Raises
    ------

        - ValueError: [description]

    Returns
    -------

        - Iterator: list of files
    """
    if settings.PROJECT_PATH is None:
        raise exceptions.ProjectNotConfiguredError()

    full_path = os.path.join(settings.PROJECT_PATH, path)
    if not os.path.isdir(full_path):
        raise ValueError('Path should be a directory')

    root, _, files = list(os.walk(full_path))[0]
    if full_path:
        files = map(lambda x: os.path.join(root, x), files)

    if func is not None:
        return map(func, files)
    
    return files
