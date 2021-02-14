import hashlib
import hmac
import logging
import os
import re
import secrets
from io import BytesIO
from mimetypes import guess_extension, guess_type
from typing import Tuple

from PIL import Image
from requests.models import Response


def create_logger(name, debug_level=logging.DEBUG, to_file=False, **kwargs):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()

    logger.addHandler(handler)
    logger.setLevel(debug_level)
    log_format = kwargs.get('log_format', '%(message)s')
    formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%S')

    if to_file:
        handler = logging.FileHandler('zineb.log')
        logger.addHandler(handler)
        handler.setFormatter(formatter)

    handler.setFormatter(formatter)
    return logger


def create_new_name(length=5):
    return secrets.token_hex(nbytes=length)


def download_image(response, download_to=None, as_thumbnail=False):
    """
    Helper for downloading images

    Parameters
    ----------
    
        response (type): an HTTP response object
        download_to (str, Optiona): download to a specific path. Defaults to None
        as_thumbnail (bool, Optional): download the image as a thumbnail. Defaults to True
    """
    from zineb.http.responses import HTMLResponse
    # from zineb.signals import pre_download

    if isinstance(response, HTMLResponse):
        response = response.cached_response
    elif isinstance(response, Response):
        response = response.content
    else:
        raise TypeError(f'The response argument requires an HTMLResponse or a Response object. Got: {response}')

    image_data = BytesIO(response)
    image = Image.open(image_data)
    
    if download_to is None:
        download_to = f'{create_new_name()}.jpg'
    else:
        download_to = f'{download_to}/{create_new_name()}.jpg'

    # pre_download.send('History', dowSnload_image, image_name=download_to)

    if as_thumbnail:
        new_image = image.copy()
        new_image.thumbnail((200,))
        new_image.save(download_to)
        return new_image.width, new_image.height

    image.save(download_to)
    return image.width, image.height, image_data


def reconstruct_url(url, pattern=None, func=None):
    if pattern is not None:
        match = re.search(pattern, url)
        if match:
            return match.groups(default=None)
    
    if func is not None:
        return func(url)

    return None


def replace_urls_suffix(urls:list, suffix, replace_with):
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
