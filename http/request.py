import re
from collections import OrderedDict
from typing import Union
from urllib import parse

import requests
from bs4 import BeautifulSoup
from pydispatch import dispatcher
from requests.models import Response
from requests.sessions import Request, Session
from w3lib.url import (is_url, safe_download_url, safe_url_string, urljoin,
                       urlparse)
from zineb import global_logger
from zineb.exceptions import RequestAborted, ResponseFailedError
from zineb.http.responses import HTMLResponse
from zineb.http.user_agent import UserAgent
from zineb.settings import settings as global_settings
from zineb.signals import signal
from zineb.tags import ImageTag, Link
from zineb.utils.conversion import transform_to_bytes

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9-_.]+@\w+\.\w+$')

USER_AGENT = UserAgent()

class BaseRequest:
    """
    Base HTTP request for all requests

    Parameters
    ----------

        url (str) url to which the request should be sent
        method (str, Optional) Request method. Defaults to GET

    Raises
    ------

        MissingSchema: the url is missing a schema
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

    def __init__(self, url: Union[Link, str, ImageTag], method='GET', **kwargs):
        self.local_logger = global_logger.new(name=self.__class__.__name__, to_file=True)

        if method not in self.http_methods:
            raise ValueError("The provided method is not valid. Should be "
            f"one of {''.join(self.http_methods)}.")

        # Calling "str" on the pseudo-url allows
        # us to get the string contained in classes
        # that represent the url such as Link or ImageTag
        url = str(url)

        session = Session()

        proxy_list = dict(set(global_settings.PROXIES))
        session.proxies.update(proxy_list)

        self.only_domains = global_settings.DOMAINS
        self.only_secured_requests = global_settings.get('ENSURE_HTTPS', False)
        self.retries = {
            'retry': global_settings.get('RETRY', False),
            'retry_times': global_settings.get('RETRY_TIMES', 2),
            'retry_http_codes': global_settings.get('RETRY_HTTP_CODES', [])
        }

        self._url_meta = None
        self.url = self._precheck_url(url)

        request = Request(method=method, url=self.url)
        self._unprepared_request = self._set_headers(request, **kwargs.get('headers', {}))

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
            self.prepared_request = session.prepare_request(self._unprepared_request)
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

    def _set_headers(self, request: Request, **extra_headers):
        headers = global_settings.get('DEFAULT_REQUEST_HEADERS', {})
        headers.update({'User-Agent': USER_AGENT.get_random_agent()})
        extra_headers.update(headers)
        request.headers = headers
        return request

    def _precheck_url(self, url: str):
        """
        Check the url respects certain specifities from the project's
        settings and other elements

        Parameters
        ----------

                url (str): a valid url

        Returns
        -------

                str: a safe url string
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

            global_logger.error(message, stack_info=True)
            raise requests.exceptions.InvalidURL(message)

        parsed_url = urlparse(url)
        self._url_meta = parsed_url

        # INFO: By default, all urls are marked as
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
                global_logger.critical(f"{url} is not secured. No HTTPS scheme is present.")
                self.can_be_sent = False

        if self.only_domains:
            if parsed_url.netloc not in self.only_domains:
                global_logger.critical((f"{url} is part of the restricted domains "
                "settings list and will not be sent. Adjust your settings if you "
                "want to prevent this security check on his domain."))
                self.can_be_sent = False
            
        return safe_url_string(url)

    def _send(self):
        """
        Sends a new HTTP request to the web
        
        Returns
        -------

                Union[Request, None] (obj): an HTTP request object
        """
        response = None

        if not self.can_be_sent:
            self.local_logger.info(("A request was not sent for the following "
            f"url {self.url} because self.can_be_sent is marked as False. Ensure that "
            "the url is not part of a restricted DOMAIN or that ENSURE_HTTPS does not"
            "force only secured requests."))
            return None

        TODO::
        # signal.send(dispatcher.Any, self, tag='Pre.Request')

        try:
            response = self.session.send(self.prepared_request)
        except requests.exceptions.HTTPError as e:
            global_logger.error(f"An error occured while processing "
            "request for {self.prepared_request}", stack_info=True)
            self.errors.append([e.args])
        except Exception as e:
            self.errors.extend([e.args])
            
        # TODO: Implement the retry
        # else:
        #     retry_codes = global_settings.RETRY_HTTP_CODES
        #     test_if_retry = [
        #         response.status_code in retry_codes,
        #         global_settings.RETRY
        #     ]
        #     if all(test_if_retry):
        #         global_logger.logger.error(f"The server response "
        #         f"returned code {response.status_code}. Will attempt "
        #         "retries if eneabled in settings file.")
        #         response = self._retry()

        if self.errors or response is None:
            raise ResponseFailedError()

        # retry = self.retries.get('retry', False)
        # if retry:
        #     retry_http_status_codes = self.retries.get('retry_http_status_codes', [])
        #     if response.status_code in retry_http_status_codes:
        #         # TODO: Might create an error
        #         response = self._retry()

        if response.status_code == 200:
            self.resolved = True

        # TODO:
        # signal.send(
        #     dispatcher.Any,
        #     self, 
        #     url=response.url, 
        #     http_response=response,
        #     tag='Post.Request'
        # )
        # policy = response.headers.get('Referer-Policy', 'origin')

        # TODO: Why set the root_url param ???
        parsed_url = urlparse(response.url)
        self.root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        return response

    def _retry(self) -> Response:
        retry_responses = []
        retry_times = self.retries.get('retry_times')
        for _ in range(0, retry_times + 2):
            response = self.session.send(self.prepared_request)
            retry_responses.extend([(response.status_code, response)])
        sorted_responses = sorted(retry_responses)
        
        other_success_codes = []
        def filter_codes(response):
            code = response[0]
            if code == 200:
                return True
            else:
                if code in other_success_codes:
                    return True
            return False
        return list(filter(filter_codes, sorted_responses))[-1]

    @classmethod
    def follow(cls, url: str):
        instance = cls(url)
        return instance._send()

    @classmethod
    def follow_all(cls, urls: Union[str, Link]):
        for url in urls:
            # FIXME: Calling str() on the url
            # allows Tags like Link to
            # be passed directly to the
            # request
            instance = cls(url)
            yield instance._send()


class HTTPRequest(BaseRequest):
    """
    Represents a basic HTTP request which wraps
    an HTMLResponse and base HTTP request

    Parameters
    ----------

        - url (str): the url to which to send the request
        - is_download_url (bool, optional): the url is going to be
          used for a download. Defaults to False.
    """
    referer = None

    def __init__(self, url: str, is_download_url=False, **kwargs):
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
                global_logger.info(f'Sent request for {self.url}')
                self._http_response = http_response
                self.html_response = HTMLResponse(
                    http_response,
                    url=self.url,
                    headers=http_response.headers
                )
                self.session.close()
            else:
                self.local_logger.error('Response failed.')
        else:
            self.local_logger.error(f'An error occured on this request: {self.url} with status code {http_response.status_code}')

    @classmethod
    def follow(cls, url: Union[str, Link]):
        instance = cls(url)
        instance._send()
        return instance.html_response

    @classmethod
    def follow_all(cls, urls: Union[str, Link]):
        for url in urls:
            yield cls.follow(url)

    def urljoin(self, path: str, use_domain=False) -> str:
        """
        To compensate for relative paths not being
        full ones, this joins the main url to the
        relative path

        Parameters
        ----------

            path (str): the relative path to use
            use_domain (bool, optional): Use the domain present
            of the in the requested url. Defaults to False.

        Returns:
            str: a valid url
        """
        if use_domain:
            return urljoin(self.root_url, str(path))
        return safe_url_string(urljoin(self._http_response.url, str(path)))


class FormRequest(BaseRequest):
    def __init__(self, url: Union[Link, str], data: dict, method: str='POST', **attrs):
        super().__init__(url, method=method)

        encoded_data = parse.urlencode(data, encoding='utf-8')
        if method == 'POST':
            self.prepared_request.headers.setdefault(b'Content-Type', b'application/x-www-form-urlencoded')
            self.prepared_request.body = transform_to_bytes(encoded_data)
        elif method == 'GET':
            url_to_get = self.prepared_request.url
            if url.endswith('?'):
                self.prepared_request.url = f"{url_to_get}{encoded_data}"
            else:
                self.prepared_request.url = f"{url_to_get}?{encoded_data}"


class FormRequestFromResponse(FormRequest):
    fields = []

    def __init__(self, form_or_soup: BeautifulSoup, url: Union[Link, str], 
                 data: dict, method='POST', **attrs):
        if form_or_soup.name != 'form':
            form_or_soup = form_or_soup.get('form')

        self._names = set()

        fields = form_or_soup.find_all('input')
        for field in fields:
            keys = field.attrs.keys()
            self._names.add(field.attrs['name'])
            base = {}
            for key in keys:
                base.setdefault(key, field.attrs[key])

        valid_data = {}
        for key, value in data.items():
            if self._has_key(key):
                valid_data.setdefault(key, value)

        super().__init__(url, valid_data, method=method, **attrs)

    def _has_key(self, key):
        return key in self._names
