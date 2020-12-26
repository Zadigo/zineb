import inspect
from collections import OrderedDict

from requests.sessions import Request, Session
from w3lib.url import urljoin
from zineb.html.tags import ImageTag, Link
from zineb.http.responses import HTMLResponse, JsonResponse
from zineb.signals import pre_request, post_request
from zineb.utils.general import create_logger


class BaseRequest:
    def __init__(self, url, **kwargs):
        self.logger = create_logger(self.__class__.__name__)

        # These are pre-check functions in case
        # we receive a BaseTags instance such as
        # Link or ImageTag
        if type(url).__name__ == 'Link' or inspect.isclass(url):
            if url.is_valid:
                url = url.href
            else:
                raise TypeError(f'The url from {repr(url)} is not valid')
        elif isinstance(url, ImageTag):
            if url.is_valid:
                url = url.src
            else:
                raise TypeError(f'The source from {repr(url)} is not valid')

        session = Session()
        self.headers = kwargs.get('headers', {})
        self._request = self._set_headers(Request(method='GET', url=url))
        prepared_request = session.prepare_request(self._request)

        self.url = url
        self.session = session
        self.prepared_request = prepared_request
        self._http_response = None
        self.resolved = False

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url}, resolved={self.resolved})"

    def __call__(self, url, *args, **kwds):
        self.__init__(url)
        self._send()
        post_request.send('SomeSignal', self)

    def _set_headers(self, request, **extra_headers):
        user_agent = pre_request.send('UserAgent', self)
        # headers = {'User-Agent': 'Zineb - v-0.0.1'}
        # extra_headers.update(headers)
        # request.headers = headers
        return request

    def _send(self):
        """Sends a new HTTP request to the web"""
        # domain_validity = pre_request.send(
        #     'ApplicationChecks', self, name='_check_domain_is_valid'
        # )
        return self.session.send(self.prepared_request)

    @classmethod
    def follow(cls, url):
        instance = cls(url)
        # headers = instance._request.headers
        # headers.update({'referer': cls.referer})
        instance._send()
        return instance

    @classmethod
    def follow_all(cls, urls):
        responses = []
        for url in urls:
            instance = cls(url)
            # headers = instance._request.headers
            # headers.update({'referer': referer})
            instance._send()
            responses.append(instance)
        return responses


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
        self.middlewares = {}
        # Use this to pass additional parameters 
        # into the HTTPRequest object
        self.options = OrderedDict()

    # def _parse_response_headers(self, response):
    #     headers = response.__dict__.get('headers')
    #     for header, value in headers.items():
    #         header = header.replace('-', '_')
    #         setattr(self, header.lower(), value)

    def _send(self):
        """Sends a new HTTP request to the web"""
        response = super()._send()
        if response.ok:
            self.logger.info(f'Sent request for {self.url}')
            self._http_response = response
            self.html_response = HTMLResponse(response, url=self.url)
            self.resolved = True
            self.session.close()

    def urljoin(self, path):
        """
        To compensate for relative paths not being
        full ones, this joins the main url to the
        relative path 
        """
        return urljoin(self._http_response.url, path)


class JsonRequest(BaseRequest):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)
        self.json_response = None

    def _send(self):
        response = super()._send()
        if response.ok:
            self._http_response = response
            self.logger.info(f'Sent request for {self.url}')
            self.json_response = JsonResponse(response, url=self.url)
            self.resolved = True
            self.session.close()
            

class FormRequest(BaseRequest):
    pass
