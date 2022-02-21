from asyncio.runners import run
from io import BytesIO
from typing import Callable, List
import asyncio
import threading
import os

from bs4 import BeautifulSoup
from PIL import Image
from zineb.settings import settings
from zineb.tags import ImageTag
from zineb.settings import lazy_settings
from zineb.utils.generate import create_new_name


def download_image_from_tag(tag, download_to=None, 
                            as_thumbnail=False, link_processor=None):
    from zineb.http.request import HTTPRequest

    if not isinstance(tag, (BeautifulSoup, ImageTag)):
        raise ValueError('Tag should be a BeautifulSoup object or an ImageTag')

    if not tag.is_valid:
        return False

    url = tag.attrs.get('src')
    if link_processor is not None:
        url = link_processor(url)

    if url is not None:
        request = HTTPRequest(url=url)
        request._send()
        return download_image(request.html_response, download_to=download_to, as_thumbnail=as_thumbnail)


def download_image_from_url(url:str, download_to: str=None, 
                            as_thumbnail: bool=False, link_processor: Callable=None):
    """Download an image using a url"""
    
    from zineb.http.request import HTTPRequest

    if link_processor is not None:
        url = link_processor(url)

    request = HTTPRequest(url=url)
    request._send()
    return download_image(request.html_response, download_to=download_to, as_thumbnail=as_thumbnail)


def download_image(response, download_to: str=None, as_thumbnail: bool=False):
    """
    Download an image using a HTTP response
    """
    from zineb.http.responses import HTMLResponse

    if isinstance(response, HTMLResponse):
        response = response.cached_response
    else:
        raise TypeError(f'The response argument requires an HTMLResponse or a Response object. Got: {response}')

    response_content = response.content
    # TODO:
    # signal.send(dispatcher.Any, response, tag='Pre.Download')
    
    buffer = BytesIO(response_content)
    image = Image.open(buffer)
    
    if download_to is None:
        # TODO: Download to the media folder
        # media_folder = getattr(lazy_settings, 'MEDIA_FOLDER')
        # if media_folder is None:
        #     download_to = f'{create_new_name()}.jpg'
        # else:
        #   download_to = os.path.join(media_folder, f'{create_new_name()}.jpg')
        download_to = f'{create_new_name()}.jpg'
    else:
        download_to = f'{download_to}/{create_new_name()}.jpg'

    if as_thumbnail:
        new_image = image.copy()
        new_image.thumbnail((200,))
        new_image.save(download_to)
        return new_image.width, new_image.height

    image.save(download_to)
    # TODO:
    # signal.send(dispatcher.Any, response, tag='Post.Download', obj=image)
    return image.width, image.height, buffer


# def async_download_images(links: List[str]):
#     def downloader(url):
#         def wrapper(*args, **kwargs):
#             width, height, buffer = download_image_from_url(url, download_to=None)
#         return wrapper
    
#     async def runner():
#         threads = []
#         for link in links:
#             threads.append(threading.Thread(target=downloader, kwargs={'url': link}))
#         return threads

#     async def main():
#         threads = await runner()
#         for thread in threads:
#             thread.start()

#     asyncio.run(main())
