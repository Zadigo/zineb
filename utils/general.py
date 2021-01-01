import logging
import os
import re
import secrets
from io import BytesIO
from typing import Tuple

from PIL import Image
from requests.models import Response
from zineb.http.responses import HTMLResponse


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


def download_image(response, download_to=None, as_thumbnail=False) -> Tuple:
    """
    Helper for downloading images

    Parameters
    ----------
    
        response (type): an HTTP response object
        chunk (int, optional): [description]. Defaults to 1024.
    """
    from zineb.signals import pre_download

    if isinstance(response, HTMLResponse):
        response = response.cached_response
    elif isinstance(response, Response):
        response = response.content
    else:
        raise TypeError('The response argument requires an HTMLResponse or a Response object')
    image_data = BytesIO(response)
    image = Image.open(image_data)

    if download_to is None:
        download_to = f'{create_new_name()}.jpg'

    # pre_download.send('History', download_image, image_name=download_to)

    if as_thumbnail:
        new_image = image.copy()
        new_image.thumbnail(200)
        new_image.save(download_to)
        return new_image.width, new_image.height, new_image.data

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
