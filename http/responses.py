from functools import cached_property
from io import BytesIO
from urllib.parse import urljoin

import pandas
from bs4 import BeautifulSoup
from PIL import Image
from w3lib.html import strip_html5_whitespace
from zineb.extractors.images import ImageExtractor
from zineb.extractors.links import LinkExtractor


class BaseResponse:
    def __init__(self, response) -> None:
        self.cached_response = response

    @cached_property
    def page_title(self):
        return strip_html5_whitespace(
            self.html_page.find('title').text
        )
    

class HTMLResponse(BaseResponse):
    """
    Represents a response transformed in a BeautifulSoup
    object for parsing.

    This class wraps not only the HTTPRequest response
    but also the transformed version of that request

    Parameters
    ----------

        response (type): a HTTP response object
    """
    def __init__(self, response, **kwargs):
        super().__init__(response)
        if isinstance(response, str):
            # Accept HTML documents as strings. Not
            # particularly necessary but can be an
            # interesting functonnality
            self.html_page = self._get_soup(response)
        else:
            try:
                self.html_page = self._get_soup(response.text)
            except:
                raise ValueError("'response' should be either a string or a response object")
        # self.response = response
        self.kwargs = kwargs

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.page_title})"

    @cached_property
    def links(self):
        extractor = LinkExtractor()
        return extractor.finalize(self.html_page)

    @cached_property
    def images(self):
        """
        Get all the images on the HTML page

        Returns
        -------

            list: list of images tags
        """
        extractor = ImageExtractor()
        return extractor.resolve(self.html_page)

    @cached_property
    def tables(self):
        return self.html_page.find_all('table')

    @staticmethod
    def _get_soup(obj):
        return BeautifulSoup(obj, 'html.parser')

    def urljoin(self, path):
        try:
            return urljoin(
                self.cached_response.url, path
            )
        except:
            return None


class ImageResponse(BaseResponse):
    def __init__(self, response):
        super().__init__(response)
        self.attrs = {}
        image, buffer = self._fit_image()
        self.image = image
        self.buffer = buffer

    def __call__(self, path):
        self.save(path)

    def _fit_image(self):
        buffer = BytesIO(self.cached_response.content)
        image = Image.open(buffer)
        height, width = image.size
        self.attrs.update({'height': height, 'width': width})
        return image, buffer

    def save(self, path=None):
        if self.image is not None:
            self.image.save(path)
        else:
            raise ValueError('Cannot save image with unset image parameter')

    def get_thumbnail(self, size):
        if self.image is not None:
            self.image.thumbnail(size, Image.ANTIALIAS)
        else:
            raise ValueError('Cannot save image with unset image parameter')


class JsonResponse(BaseResponse):
    pass
    # def __init__(self, response):
    #     super().__init__(response)
    #     try:
    #         response = response.json()
    #     except:
    #         response = None

    #     if isinstance(response, dict):
    #         pd = pandas.DataFrame()
    #         self.response = pd.from_dict(response, orient='records')
