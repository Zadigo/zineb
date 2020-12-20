import logging
import os
from io import BytesIO
from PIL import Image
import secrets

from requests.models import Response
from zineb.http.responses import HTMLResponse


def create_logger(name, **kwargs):
    logs = logging.getLogger(name)
    logs.addHandler(logging.StreamHandler())
    logs.level = logging.DEBUG

    log_format = kwargs.get('log_format', None)
    if log_format is not None:
        handler = logging.Formatter(log_format)
        logs.addHandler(handler)

    return logs


def create_new_name():
    return secrets.token_hex(nbytes=5)


def download_image(response, download_to=None, as_thumbnail=False):
    """
    Helper for downloading images

    Parameters
    ----------
    
        response (type): an HTTP response object
        chunk (int, optional): [description]. Defaults to 1024.
    """
    if isinstance(response, HTMLResponse):
        response = response.cached_response
    elif isinstance(response, Response):
        response = response.content
    else:
        raise TypeError(
            'The response argument requires an HTMLResponse or a Response object'
        )
    image_data = BytesIO(response)
    image = Image.open(image_data)

    if as_thumbnail:
        new_image = image.copy()
        return new_image.thumbnail(200)

    if download_to is None:
        download_to = f'{secrets.token_hex(nbytes=5)}.jpg'

    image.save(download_to)
    return image.width, image.height, image_data
