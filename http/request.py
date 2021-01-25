import inspect
import random
from collections import OrderedDict

from pydispatch import dispatcher
from requests.sessions import Request, Session
from w3lib.url import safe_url_string, urljoin, urlparse
from zineb.http.responses import HTMLResponse, JsonResponse
from zineb.http.user_agent import UserAgent
from zineb.signals import Signal, signal
from zineb.tags import ImageTag, Link
from zineb.utils.general import create_logger

logger = create_logger('BaseRequest')

pre_request = Signal()
post_request = Signal()


class BaseRequest:
    """
    Base HTTP request for all requests

    Parameters
    ----------

        url (str) url to which the request should be sent
        method (str, Optional) Request method. Defaults to GET

    Raises
    ------

        TypeError: [description]
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

    def __init__(self, url, method='GET', **kwargs):
        if isinstance(url, Link):
            url = url.href
        elif inspect.isclass(url):
            url = url.href
        elif isinstance(url, ImageTag):
            url = url.src
        else:
            url = url

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

        self.session = session
        self.prepared_request = session.prepare_request(self._unprepared_request)
        self._http_response = None
        # Whether the request was
        # sent or not
        self.resolved = False

        signal.connect(self, signal='Request-Before')
        signal.connect(self, signal='Request-After')

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url}, resolved={self.resolved})"

    def __call__(self, sender, **kwargs):
        # print(sender, kwargs)
        pass

    def _set_headers(self, request, **extra_headers):
        user_agent = UserAgent()

        headers = {
            # 'Accept-Language': 'en-US,en-GB,fr-FR;q=0.9,q=0.8,q=0.7',
            # 'Accept-Encoding': 'br,gzip,deflate,compress',
            'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': user_agent.get_random_agent(),
            'Referrer': 'https://google.com',
            # 'Referer-Policy': 'strict-origin-when-cross-origin'
        }
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
        parsed_url = urlparse(url)

        scheme = parsed_url[0]
        netloc = parsed_url[1]

        if self.only_secured_requests:
            if scheme != 'https' or scheme != 'ftps':
                logger.critical(f'{url} is not secured. No HTTPS scheme is present')
                self.can_be_sent = False

        if self.only_domains:
            if netloc in self.only_domains:
                logger.critical(f'{url} is part of the restricted domains list and will not be able to be sent')
                self.can_be_sent = False
            
        return safe_url_string(url)

    def _send(self):
        """Sends a new HTTP request to the web"""
        class_name = self.__class__.__name__
        # pre_request.send('Request.Before', self)
        response = self.session.send(self.prepared_request)

        retry = self.retries.get('retry', False)
        if retry:
            retry_http_status_codes = self.retries.get('retry_http_status_codes', [])
            if response.status_code in retry_http_status_codes:
                response = self._retry()

        if response.status_code == 200:
            self.resolved = True

        result = signal.send(
            'Zineb-History', 
            class_name, 
            url=response.url, 
            http_response=response,
            http_instance=self
        )
        # policy = response.headers.get('Referer-Policy', 'origin')
        return response

    def _retry(self):
        retry_times = self.retries.get('retry_times')
        for _ in range(0, retry_times + 2):
            return self.session.send(self.prepared_request)

    @classmethod
    def follow(cls, url):
        instance = cls(url)
        instance._send()
        return instance

    @classmethod
    def follow_all(cls, urls):
        for url in urls:
            # Calling str() on the url
            # allows Tags like Link to
            # be passed directly to the
            # request
            instance = cls(str(url))
            instance._send()
            yield instance


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
        # self.middlewares = {}
        # Use this to pass additional parameters 
        # into the HTTPRequest object
        self.options = OrderedDict()

    def _send(self):
        """Sends a new HTTP request to the web"""
        response = super()._send()
        if response.ok:
            logger.info(f'Sent request for {self.url}')
            self._http_response = response
            self.html_response = HTMLResponse(response, url=self.url, headers=response.headers)
            self.session.close()

    def urljoin(self, path):
        """
        To compensate for relative paths not being
        full ones, this joins the main url to the
        relative path 
        """
        return urljoin(self._http_response.url, str(path))


class JsonRequest(BaseRequest):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.json_response = None

    def _send(self):
        response = super()._send()
        if response.ok:
            self._http_response = response
            logger.info(f'Sent request for {self.url}')
            self.json_response = JsonResponse(response, url=self.url)
            self.resolved = True
            self.session.close()
            

class FormRequest(BaseRequest):
    def __init__(self, url, **kwargs):
        super().__init__(url, method='POST', **kwargs)
