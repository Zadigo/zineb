import re
from collections import OrderedDict
from typing import Union
import time
from urllib import parse

import requests
from requests.sessions import Request, Session
from w3lib.url import is_url, safe_download_url, safe_url_string, urlparse

from zineb.exceptions import ResponseFailedError
from zineb.http.responses import HTMLResponse
from zineb.http.user_agent import UserAgent
from zineb.logger import Logger
from zineb.settings import settings
from zineb.tags import Link
from zineb.utils.conversion import transform_to_bytes

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9-_.]+@\w+\.\w+$')

USER_AGENT = UserAgent()


class BaseRequest:
    """
    Base HTTP request for all requests
    """
    only_secured_requests = False
    only_domains = []
    # Indicates whether the HTTPRequest can be sent
    # if all the prechecks on the url turn out to
    # be positive -; this is a non blocking procedure
    # leaving the front end spider to deal with
    # .. Also, assumes that all created requests
    # can be sent as is
    can_be_sent = True
    http_methods = ['GET', 'POST']

    def __init__(self, url, method='GET', **kwargs):
        self.local_logger = Logger(self.__class__.__name__)

        if method not in self.http_methods:
            raise ValueError("The provided method is not valid. Should be "
                             f"one of {''.join(self.http_methods)}.")

        # Calling "str" on the pseudo-url allows
        # us to get the string contained in classes
        # that represent an url such as Link or ImageTag
        url = str(url)

        session = Session()

        proxy_list = dict(set(settings.PROXIES))
        session.proxies.update(proxy_list)

        self.only_domains = settings.DOMAINS
        self.only_secured_requests = settings.get('ENSURE_HTTPS', False)

        self._url_meta = None
        self.url = self._precheck_url(url)

        request = Request(method=method, url=self.url)
        self._unprepared_request = self._set_headers(
            request, **kwargs.get('headers', {}))

        # Use this error class to add any errors that
        # would have occured during the HTTP request
        # session
        self.errors = []

        self.session = session
        try:
            # Sometimes malformed urls are passed by accident
            # in this section which breaks the application completely
            # with a MissingSchema error and maybe instead of breaking the
            # whole process for just one badly formed url, just pass that
            # given url and use the self.resolved flag to determine if
            # a request should indeed be sent with the given class
            self.prepared_request = session.prepare_request(
                self._unprepared_request)
        except requests.exceptions.MissingSchema as e:
            self.errors.extend([e.args])
        except Exception as e:
            self.errors.extend([e.args])

        self.resolved = False
        self._http_response = None

        self.domain = self._url_meta.netloc
        self.root_url = None

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url}, resolved={self.resolved})"

    @classmethod
    def follow(cls, url):
        instance = cls(str(url))
        instance._send()
        return instance

    @classmethod
    def follow_all(cls, urls):
        for url in urls:
            # Calling str() on the url
            # allows Tags like Link to
            # be passed directly to the
            # request
            yield cls.follow(url)

    def _set_headers(self, request, **extra_headers):
        headers = settings.get('DEFAULT_REQUEST_HEADERS', {})

        user_agent = USER_AGENT.get_random_agent()
        headers.update({'User-Agent': user_agent})

        extra_headers.update(headers)
        request.headers = headers
        return request

    def _precheck_url(self, url):
        """
        Check the url respects certain specifities from the project's
        settings and other elements
        """
        # Check if we're trying to send a request
        # to an email address
        if EMAIL_REGEX.match(url):
            message = "You are trying to send a request to an email address."
            raise requests.exceptions.InvalidSchema(message)

        if not is_url(url):
            # TODO: When using https:// this returns True
            # when this is not even a real URL
            message = (f"The url that was provided is not valid. Got: {url}.")
            self.local_logger.instance.error(message, stack_info=True)
            raise requests.exceptions.InvalidURL(message)

        parsed_url = urlparse(url)
        self._url_meta = parsed_url

        # NOTE: By default, all urls are marked as
        # can be sent UNLESS they do not meet two
        # criterium present in the settings files.
        # The url is part of a restricted domain
        # or the url is not secured (no https
        # or ftps scheme)

        if self.only_secured_requests:
            # TODO: Logic for FTPS
            # logic = [
            #     parsed_url.scheme != 'https',
            #     parsed_url.scheme != 'ftps'
            # ]
            # if not all(logic):

            if 'https' not in parsed_url.scheme:
                self.local_logger.instance.critical(
                    f"{url} is not secured. No HTTPS scheme is present.")
                self.can_be_sent = False

        if self.only_domains:
            if parsed_url.netloc not in self.only_domains:
                self.local_logger.instance.critical((f"{url} is not a memeber of the allowed "
                                                     "domains settings list and will not be sent. Adjust your settings if you "
                                                     "want to prevent this security check on his domain."))
                self.can_be_sent = False

        return safe_url_string(url)

    def _send(self):
        response = None

        if not self.can_be_sent:
            self.local_logger.instance.logger.info(("A request cannot be sent for the following "
                                                    f"url {self.url} because self.can_be_sent is marked as False. Ensure that "
                                                    "the url is not part of a restricted DOMAIN or that ENSURE_HTTPS does not"
                                                    "force only secured requests."))
            return None

        # TODO: Send signal before the request
        # is sent by the class

        try:
            response = self.session.send(self.prepared_request)
        except requests.exceptions.HTTPError as e:
            self.local_logger.instance.logger.error(f"An error occured while processing "
                                                    "request for {self.prepared_request}", stack_info=True)
            self.errors.append([e.args])
        except Exception as e:
            self.errors.extend([e.args])

        if self.errors or response is None:
            raise ResponseFailedError(self.errors)

        if response.status_code == 200:
            self.resolved = True

        # TODO: Send signal after the request
        # was sent by the class

        parsed_url = urlparse(response.url)
        # Factually this represents the domain. This
        # is done afterwards because we know by then
        # that the url was valid
        self.root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # time.sleep(settings.RATE_LIMIT)
        return response


class HTTPRequest(BaseRequest):
    """
    Represents a basic HTTP request and overall proxy
    for an `HTMLResponse` and a `requests.Request`
    instance

    Example
    -------

    Sending a basic request can be done in the followin way:

    >>> instance = HttpRequest('http://example.com')
    ... instance._send()

    You can also follow additional links using these methods:

    >>> new_instance = instance.follow('http://example.com/1')
    ... new_instance = instance.follow_all(['http://example.com/2'])

    Finally, you can also join a relative path to the url's domain

    >>> new_url = instance.urljoin('kendall')
    ... 'http://example.com/kendall'
    ... instance.follow(new_url)
    """
    referer = None

    def __init__(self, url, is_download_url=False, **kwargs):
        super().__init__(url, **kwargs)
        self.html_response = None
        self.counter = kwargs.get('counter', 0)

        is_download_url = kwargs.get('is_download_url', False)
        if is_download_url:
            url = safe_download_url(url)

        # Use this to pass additional parameters
        # into the HTTPRequest object
        self.options = OrderedDict()

    def _send(self):
        """
        Sends a new HTTP request to the web
        """
        http_response = super()._send()
        if http_response is not None:
            if http_response.ok:
                self.local_logger.instance.info(f'Sent request for {self.url}')
                self._http_response = http_response
                self.html_response = HTMLResponse(
                    http_response,
                    url=self.url,
                    headers=http_response.headers
                )
                self.session.close()
            else:
                response_code = http_response.status_code
                self.local_logger.instance.error(
                    f'Response failed with code {response_code}.')
        else:
            self.local_logger.instance.error(
                f'An error occured on this request: {self.url} with status code {http_response.status_code}')

    def urljoin(self, path, use_domain=False):
        """
        To compensate for relative paths not being
        full ones, this helper function joins a main url 
        to a relative path
        """
        if use_domain:
            return parse.urljoin(self.root_url, str(path))
        return safe_url_string(parse.urljoin(self._http_response.url, str(path)))

    def json(self, sort_by=None, filter_func=None):
        """If the expected response is not an HTML object, 
        return the JSON content via this method"""
        if self.html_response.headers.is_json_response:
            result = self.html_response.cached_response.json()
            if sort_by is not None:
                return sorted(result, key=lambda x: x[sort_by])
            return result
        return {}


class FormRequest(BaseRequest):
    def __init__(self, url: Union[Link, str], data: dict, method: str = 'POST', **attrs):
        super().__init__(url, method=method)

        encoded_data = parse.urlencode(data, encoding='utf-8')
        if method == 'POST':
            self.prepared_request.headers.setdefault(
                b'Content-Type', b'application/x-www-form-urlencoded')
            self.prepared_request.body = transform_to_bytes(encoded_data)
        elif method == 'GET':
            url_to_get = self.prepared_request.url
            if url.endswith('?'):
                self.prepared_request.url = f"{url_to_get}{encoded_data}"
            else:
                self.prepared_request.url = f"{url_to_get}?{encoded_data}"


class SitemapRequest(BaseRequest):
    """A special request for working 
    with sitemaps"""


# class FormRequestFromResponse(FormRequest):
#     fields = []

#     def __init__(self, form_or_soup: BeautifulSoup, url: Union[Link, str],
#                  data: dict, method='POST', **attrs):
#         if form_or_soup.name != 'form':
#             form_or_soup = form_or_soup.get('form')

#         self._names = set()

#         fields = form_or_soup.find_all('input')
#         for field in fields:
#             keys = field.attrs.keys()
#             self._names.add(field.attrs['name'])
#             base = {}
#             for key in keys:
#                 base.setdefault(key, field.attrs[key])

#         valid_data = {}
#         for key, value in data.items():
#             if self._has_key(key):
#                 valid_data.setdefault(key, value)

#         super().__init__(url, valid_data, method=method, **attrs)

#     def _has_key(self, key):
#         return key in self._names
