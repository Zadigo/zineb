from collections import ChainMap
from functools import cached_property
from io import BytesIO
from itertools import chain
from mimetypes import guess_extension
from typing import Any, Union
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from bs4.element import Tag
from PIL import Image
from w3lib.html import strip_html5_whitespace
from w3lib.url import is_url

from zineb.extractors.base import (ImageExtractor, LinkExtractor,
                                   MultiTablesExtractor)
from zineb.http.headers import ResponseHeaders
from zineb.utils.generate import create_new_name, random_string


class BaseResponse:
    def __init__(self, response):
        self.cached_response = response
        self.headers = ResponseHeaders(response.headers)


class HTMLResponse(BaseResponse):
    """
    Represents a response transformed in a BeautifulSoup
    object for parsing

    This class wraps not only the HTTPRequest response
    but also the transformed version of that request

    Parameters
    ----------

        - response (Response): an HTTP response object

    Example
    -------
            
        >>> instance = HTMLResponse(response)
        ... instance.html_page
        ... link_object = instance.find("a")
    """

    def __init__(self, response, **kwargs):
        # PERFORMANCE: Import this module during
        # the __init__ because this takes a little
        # bit of time to load
        from requests.models import Response

        super().__init__(response)

        if isinstance(response, str):
            self.html_page = self._get_soup(response)
        elif isinstance(response, Response):
            self.html_page = self._get_soup(response.text)
        elif isinstance(response, HTMLResponse):
            # There perhaps be an occurence where someone passes
            # an instance of HTMLResponse as resposne here and
            # perhaps this functionality can be kept (?)
            self.html_page = self._get_soup(response.cached_response.text)
            self.cached_response = response.cached_response
        else:
            raise ValueError((f"Response should be either an html string, "
            "a zineb.requests.HTTPRequest object or a zineb.responses.HTMLResponse "
            "instance. Instead got {response}"))

        self.kwargs = kwargs.copy()
        # Indicates whether the request was completed
        # with a status code of 200
        # self.completed = True

    def __getattr__(self, name) -> Union[Tag, Any]:
        soup_attributes = dir(self.html_page)
        if name in soup_attributes:
            return getattr(self.html_page, name)
        return name

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.page_title})"

    @property
    def page_title(self) -> str:
        return strip_html5_whitespace(
            self.html_page.find('title').text
        )

    @cached_property
    def links(self):
        """
        Get all the links present on the HTML page
        """
        extractor = LinkExtractor()
        extractor.resolve(self.html_page)
        return extractor.validated_links

    @cached_property
    def images(self):
        """
        Get all the images on the HTML page
        """
        extractor = ImageExtractor()
        return extractor.resolve(self.html_page)

    @cached_property
    def tables(self):
        extractor = MultiTablesExtractor(
            has_headers=True, filter_empty_rows=True
        )
        extractor.resolve(self.html_page)
        return extractor

    @staticmethod
    def _get_soup(obj):
        return BeautifulSoup(obj, 'html.parser')

    @staticmethod
    def _writer(content):
        name = f"{random_string(length=5)}.html"
        # TODO: Send a signal once the content of
        # the response was written to a file

        with open(name, mode='w', encoding='utf-8') as f:
            f.write(content)

    def urljoin(self, path):
        return urljoin(self.cached_response.url, str(path))

    def download_html_page(self):
        self._writer(self.html_page.find('html').html)

    def download_html_page_text(self):
        self._writer(self.html_page.find('html').text)


class ImageResponse(BaseResponse):
    """
    Represents a response for an image 

    Parameters
    ----------

        Response (type): zineb.responses.Response
    """
    def __init__(self, response):
        super().__init__(response)
        self.attrs = {}

        content_type = response.headers.get('Content-Type')
        extension = guess_extension(content_type)

        images_extensions = ['.jpg', '.png']
        if extension not in images_extensions:
            raise ValueError('Response does not have an image Content-Type in the headers')
        self.extension = extension
        
        image, buffer = self._fit_image(response)
        self.image = image
        self.buffer = buffer

    def __call__(self, path):
        self.save(path)

    def _fit_image(self, response):
        """
        Passes the content of the response to a buffer and
        Pythonizes the content as PIL Image Python object

        Parameters
        ----------

            response (Response): an HTTP response

        Returns
        -------

            tuple: (PIL, buffer)
        """
        buffer = BytesIO(response.content)
        image = Image.open(buffer)
        height, width = image.size
        self.attrs.update({'height': height, 'width': width})
        return image, buffer

    def save(self, path=None):
        if path is not None:
            path = f'{path}/{create_new_name()}'
        else:
            path = create_new_name()
        self.image.save(f'{path}.{self.extension}')
        # if self.image is not None:
        # else:
        #     raise ValueError('Cannot save image with unset image parameter')

    def get_thumbnail(self, size: tuple):
        if self.image is not None:
            self.image.thumbnail(size, Image.ANTIALIAS)
        else:
            raise ValueError('Cannot save image with unset image parameter')


class JsonResponse(BaseResponse):
    """__init__ [summary]

    [extended_summary]

    Args:
        response (requests.Response): [description]

    Raises:
        ValueError: [description]
        TypeError: [description]
    """
    def __init__(self, response, **kwargs):
        import pandas
        
        super().__init__(response)
        content_type = self.headers.get('content-type')
        if 'application/json' not in content_type:
            raise ValueError(("Response does not have an 'application/json' "
            "content-type header in its headers"))

        try:
            self.raw_data = response.json()
        except:
            raise TypeError('Response should be an HTTP request response (requests.models.Response)')
        self.response_data = pandas.DataFrame(data=self.raw_data)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.raw_data})'

    def __str__(self):
        return str(self.raw_data)

    def __add__(self, b):
        return self.raw_data + b.raw_data

    def __getitem__(self, index):
        return self.raw_data[index]

    @cached_property
    def columns(self):
        return self.response_data.columns

    def links(self, unique=False):
        """
        Retrieve all the links within the JSON element

        Parameters
        ----------

            unique (bool, optional): links should be unique. Defaults to False.

        Returns
        -------

            list: list of all the links
        """
        link_mappings = []

        def check_if_url(value):
            if isinstance(value, str):
                return is_url(value)
            return False

        for item in self.raw_data:
            values = filter(lambda x: check_if_url(x), item.values())
            link_mappings.append(list(values))
        flattened_links = ChainMap(*link_mappings)
        if unique:
            return {link for link in flattened_links}
        return list(flattened_links)

    def emails(self):
        """
        Return every email within the JSON response

        Returns
        -------

            (set): a set of emails from the response
        """
        email_mappings = []

        def check_if_email(value):
            if isinstance(value, str):
                return all(['@' in value])
            return False

        for item in self.raw_data:
            values = filter(lambda x: check_if_email(x), item.values())
            email_mappings.append(values)
        flattened_emails = chain(*email_mappings)
        return {email for email in flattened_emails}

    def get_response_from_key(self, key):
        """
        There might be cases when you would like to create a
        DataFrame starting from a specific key in the dict

        Parameters
        ----------

            key (str): a key within the dictionnary

        Raises
        ------

            KeyError: [description]

        Returns
        -------

            DataFrame: a pandas DataFrame
        """
        import pandas
        try:
            return pandas.DataFrame(data=self.raw_data[key])
        except:
            raise KeyError('The given key does not exist on the response')


class XMLResponse(BaseResponse):
    pass
