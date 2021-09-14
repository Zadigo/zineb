from io import BytesIO
from typing import Callable

from bs4 import BeautifulSoup
from PIL import Image
from pydispatch import dispatcher
from zineb.signals import signal
from zineb.utils.generate import create_new_name


def download_image_from_tag(tag: BeautifulSoup, download_to=None, 
                            as_thumbnail=None, link_processor=None):
    from zineb.http.request import HTTPRequest

    url = tag.attrs.get('src')
    if link_processor is not None:
        url = link_processor(url)
    if url is not None:
        request = HTTPRequest(url=url)
        request._send()
        return download_image(request.html_response, download_to=download_to, as_thumbnail=as_thumbnail)


def download_image_from_url(url:str, download_to=None,
                            as_thumbnail=None, link_processor: Callable=None):
    from zineb.http.request import HTTPRequest

    if link_processor is not None:
        url = link_processor(url)
    request = HTTPRequest(url=url)
    request._send()
    return download_image(request.html_response, download_to=download_to, as_thumbnail=as_thumbnail)


def download_image(response, download_to=None, as_thumbnail=False):
    """
    Downloads a single image to the media folder

    Parameters
    ----------
    
        response (Type): an HTTP response object
        download_to (String, Optiona): download to a specific path. Defaults to None
        as_thumbnail (Bool, Optional): download the image as a thumbnail. Defaults to True
    """
    from zineb.http.responses import HTMLResponse

    if isinstance(response, HTMLResponse):
        response = response.cached_response
    else:
        raise TypeError(f'The response argument requires an HTMLResponse or a Response object. Got: {response}')

    response_content = response.content
    signal.send(dispatcher.Any, response, tag='Pre.Download')
    
    buffer = BytesIO(response_content)
    image = Image.open(buffer)
    
    if download_to is None:
        download_to = f'{create_new_name()}.jpg'
    else:
        download_to = f'{download_to}/{create_new_name()}.jpg'

    if as_thumbnail:
        new_image = image.copy()
        new_image.thumbnail((200,))
        new_image.save(download_to)
        return new_image.width, new_image.height

    image.save(download_to)
    signal.send(dispatcher.Any, response, tag='Post.Download', obj=image)
    return image.width, image.height, buffer
