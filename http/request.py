import random
from collections import OrderedDict
from typing import Union

import requests
from pydispatch import dispatcher
from requests.models import Response
from requests.sessions import Request, Session
from w3lib.url import (is_url, safe_download_url, safe_url_string, urljoin,
                       urlparse)
from zineb import global_logger
from zineb.http.responses import HTMLResponse, JsonResponse
from zineb.http.user_agent import UserAgent
from zineb.signals import signal
from zineb.tags import ImageTag, Link


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
    # .. Also, assume that all created requests
    # can be sent as is
    can_be_sent = True
    project_settings = {}

    def __init__(self, url: Union[Link, str, ImageTag], method='GET', **kwargs):
        # Calling "str" on the pseudo-url allows
        # us to get the string contained in classes
        # that represent the url such as Link or ImageTag
        url = str(url)

        self.project_settings = kwargs.get('settings', {})

        session = Session()
        proxies = self.project_settings.get('proxies')
        if proxies is not None:
            http_proxies = list(filter(lambda x: 'http' in x, proxies))
            https_proxies = list(filter(lambda x: 'https' in x, proxies))
            proxy_map = {
                'http': random.choice(http_proxies)
            }
            if http_proxies:
                proxy_map.update({'http': random.choice(http_proxies)})

            if https_proxies:
                proxy_map.update({'https': random.choice(https_proxies)})

        self.only_domains = self.project_settings.get('DOMAINS')
        self.only_secured_requests = self.project_settings.get('ENSURE_HTTPS')
        self.retries = {
            'retry': self.project_settings.get('RETRY', False),
            'retry_times': self.project_settings.get('RETRY_TIMES', 2),
            'retry_http_codes': self.project_settings.get('RETRY_HTTP_CODES', [])
        }

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

        # Whether the request was
        # sent or not
        self.resolved = False
        self._http_response = None

        self.domain = None

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url}, resolved={self.resolved})"

    def _set_headers(self, request: Request, **extra_headers):
        user_agent = UserAgent()
        # This is a specific technique that allows
        # to call the HTTPRequest class without
        # having to pass or use the full project
        # settings
        if self.project_settings:
            headers = self.project_settings.DEFAULT_REQUEST_HEADERS
        else:
            from zineb.settings import settings as global_settings
            headers = global_settings.get('DEFAULT_REQUEST_HEADERS', {})
        headers.update({'User-Agent': user_agent.get_random_agent()})
        extra_headers.update(headers)
        request.headers = headers
        return request

    def _precheck_url(self, url):
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
        if not is_url(url):
            message = f"The url that was provided is not valid. Got: {url}"
            global_logger.error(message, stack_info=True)
            raise requests.exceptions.InvalidURL(message)

        parsed_url = urlparse(url)

        scheme = parsed_url[0]
        netloc = parsed_url[1]

        if self.only_secured_requests:
            if scheme != 'https' or scheme != 'ftps':
                global_logger.critical(f"{url} is not secured. No HTTPS scheme is present")
                self.can_be_sent = False

        if self.only_domains:
            if netloc in self.only_domains:
                global_logger.critical(f"{url} is not part of the restricted domains list and will not be able to be sent")
                self.can_be_sent = False
            
        return safe_url_string(url)

    def _send(self):
        """
        Sends a new HTTP request to the web
        
        Returns
        -------

                Request (obj): an HTTP request object
        """
        response = None
        signal.send(dispatcher.Any, self, tag='Pre.Request')

        try:
            response = self.session.send(self.prepared_request)
        except requests.exceptions.HTTPError as e:
            global_logger.error(f"An error occured while processing request for {self.prepared_request}", stack_info=True)
            self.errors.append([e.args])
        except Exception as e:
            self.errors.extend([e.args])
        else:
            retry = self.retries.get('retry', False)
            if retry:
                retry_http_status_codes = self.retries.get('retry_http_status_codes', [])
                if response.status_code in retry_http_status_codes:
                    # TODO: Might create an error
                    response = self._retry()

            if response.status_code == 200:
                self.resolved = True

        signal.send(
            dispatcher.Any,
            self, 
            url=response.url, 
            http_response=response,
            tag='Post.Request'
        )
        # policy = response.headers.get('Referer-Policy', 'origin')

        parsed_url = urlparse(response.url)
        self._domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

        return response

    def _retry(self) -> Response:
        retry_responses = []
        retry_times = self.retries.get('retry_times')
        for _ in range(0, retry_times + 2):
            # return self.session.send(self.prepared_request)
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
    def follow(cls, url):
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

            url (str): the url to which to send the request
    """
    referer = None

    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.html_response = None
        self.counter = kwargs.get('counter', 0)

        is_download_url = kwargs.get('is_download_url', False)
        if is_download_url:
            url = safe_download_url(url)
            
        # Use this to pass additional parameters 
        # into the HTTPRequest object
        self.options = OrderedDict()

    # def __getattr__(self, key):
    #     if key == 'html_response':
    #         value = getattr(self, key)
    #         if value is None:
    #             raise ValueError("You should call _send on the request before accessing the html_response")
    #     return super().__getattr__(key)

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
                    http_response, url=self.url, headers=http_response.headers
                )
                self.session.close()
        else:
            global_logger.error(f'An error occured on this request: {self.url}')

    @classmethod
    def follow(cls, url: Union[str, Link]):
        instance = cls(url)
        instance._send()
        return instance.html_response

    @classmethod
    def follow_all(cls, *urls: Union[str, Link]):
        for url in urls:
            # instance = cls(url)
            # instance._send()
            # yield instance.html_response
            yield cls.follow(url)

    def urljoin(self, path: str, use_domain=False):
        """
        To compensate for relative paths not being
        full ones, this joins the main url to the
        relative path 
        """
        if use_domain:
            return urljoin(self._domain, str(path))
        return urljoin(self._http_response.url, str(path))


class JsonRequest(BaseRequest):
    def __init__(self, url: Union[str, Link], **kwargs):
        super().__init__(url, **kwargs)
        self.json_response = None

    def _send(self):
        response = super()._send()
        if response.ok:
            self._http_response = response
            global_logger.info(f'Sent request for {self.url}')
            self.json_response = JsonResponse(response, url=self.url)
            self.resolved = True
            self.session.close()
            

class FormRequest(BaseRequest):
    def __init__(self, url: Union[Link, str], **attrs):
        super().__init__(url, method='POST')
