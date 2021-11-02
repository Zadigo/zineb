import os
import warnings
# import time
from collections import OrderedDict
from io import StringIO
from typing import Iterator, Union

from bs4 import BeautifulSoup

# from xml.etree import ElementTree
from zineb import global_logger, signals
# from zineb.http.pipelines import CallBack
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse, JsonResponse, XMLResponse
from zineb.settings import settings as global_settings
from zineb.utils.formatting import LazyFormat

# from pydispatch import dispatcher



class BaseSpider(type):
    def __new__(cls, name, bases, attrs):
        create_new = super().__new__
        if not bases:
            return create_new(cls, name, bases, attrs)

        spider_options = OrderedDict()
        if 'Meta' in attrs:
            _meta = attrs.pop('Meta')
            options = _meta.__dict__

            allowed_options = ['domains', 'base_url', 'verbose_name', 'sorting', 'limit_requests_to']
            for key, option in options.items():
                if not key.startswith('__'):
                    if key in allowed_options:
                        spider_options.setdefault(key, option)
                    else:
                        raise ValueError((f"Meta received an invalid option: '{key}'. "
                        f"Authorized options are {', '.join(allowed_options)}"))
        attrs.update({'_meta': spider_options})

        if 'start_urls' in attrs:            
            new_class = create_new(cls, name, bases, attrs)

            start_urls = getattr(new_class, 'start_urls')
            if not start_urls:
                warnings.warn("No start urls were provided for the spider", Warning, stacklevel=0)

            prepared_requests = attrs.get('_prepared_requests', [])
            for index, link in enumerate(start_urls):
                request = HTTPRequest(link, counter=index)
                prepared_requests.append(request)
            setattr(new_class, '_prepared_requests', prepared_requests)
            return new_class
        return create_new(cls, name, bases, attrs)


class Spider(metaclass=BaseSpider):
    """
    To run a spider, you first need to inherit
    from this class. You also need to implement
    a list of starting urls

    Example
    -------

        class Spider(Model):
            start_urls = [
                'http://example.com'
            ]

            def start(self, response, **kwargs):
                ...

    Parameters
    ----------

        configuration (dict, optional): A set of additional default values. Defaults to None
    """
    _prepared_requests = []
    start_urls = []

    def __init__(self, **kwargs):
        global_logger.info(f'Starting {self.__class__.__name__}')
        global_logger.info(f"{self.__class__.__name__} contains {self.__len__()} request(s)")
        # Tell all middlewares and signals registered
        # to receive Any that the Spider is ready
        # and fully loaded
        # TODO:
        # signal.send(dispatcher.Any, self, tag='Pre.Start')

        self._cached_aggregated_results = None
        self._cached_aggregated_results = self._resolve_requests(debug=kwargs.get('debug', False))

    def __len__(self):
        return len(self._prepared_requests)

    def __repr__(self):
        return f"{self.__class__.__name__}(requests={self.__len__()})"

    # def _resolve_return_containers(self, containers):
    #     from zineb.models.pipeline import ModelsPipeline
    #     if not containers or containers is None:
    #         return False

    #     callbacks = filter(lambda k: isinstance(k, CallBack), containers)
    #     pipes = list(filter(lambda p: isinstance(p, ModelsPipeline), containers))

    #     if pipes:
    #         pipe = ModelsPipeline(pipes)
    #         return pipe._resolve_dataframes()

    def _resolve_requests(self, debug=False):
        """
        Call `_send` each requests and pass the response in
        the start method of the same class

        Parameters
        ----------

            debug (Bool): determines whether to send the 
            requests or not. Defaults to False.
        """
        if self._prepared_requests:
            if not debug:
                limit_requests_to = self._meta.get('limit_requests_to', len(self._prepared_requests))

                for i in range(0, limit_requests_to):
                    request = self._prepared_requests[i]
                    request._send()

                    soup_object = request.html_response.html_page
                    self.start(
                        request.html_response,
                        request=request,
                        soup=soup_object
                    )

                    # TODO: Work with return values from
                    # from the functions
                    # return_values_container = deque() 
                    # return_value = self.start()
                    # if return_value is not None:
                    #     return_values_container.append(return_value)

                # TODO:
                # signal.send(dispatcher.Any, self, tag='Post.Initial.Requests', urls=self._prepared_requests)
                # return self._resolve_return_containers(return_values_container)
            else:
                global_logger.logger.warn(f'You are using {self.__class__.__name__} in DEBUG mode')

    def start(self, response: Union[HTMLResponse, JsonResponse, XMLResponse], request: HTTPRequest=None, **kwargs):
        """
        Use this function as an entrypoint to scrapping
        your HTML page. This method gets called on the
        initialization of the web spider

        Each response is iterated over and passed through
        this function in addition with the request

        Parameters
        ----------

            response (HTMLResponse): an HTMLResponse object
            
            In addition to the response, these objects are also
            passed in the kwargs parameter:

                request (HTTPRequest): the HTTPRequest object 
                soup (BeautifulSoup): the beautiful soup object

                def start(self, response, request=None, soup=None):
                    pass
        """
        pass


class Zineb(Spider):
    """
    This is the base class that spiders need to
    subclass in order to implement a spider
    for a scrapping project
    """


class SitemapCrawler(Spider):
    """
    Use this class in order to scrap from a
    websites' sitemaps
    """


class FileCrawler:
    """
    This is a kind of spider that can crawl files locally and then eventually
    perform requests to the web in order to implement additional data.

    In order to use this spider efficiently, you need a have local HTML
    files that will be be opened sequentially and then parsed according to
    the logic provided in the `start` function
    """
    start_files = []
    root_dir = None

    def __init__(self):
        self.buffers = []

        start_files = list(self.start_files)

        # If the root_dir is not set, then
        # default to the default
        # 'media' folder
        if self.root_dir is None:
            self.root_dir = 'media'

        def create_full_path(path):
            result = os.path.join(global_settings.PROJECT_PATH, self.root_dir, path)

            if not os.path.isfile(result):
                raise ValueError(LazyFormat('Path does not point to a valid '
                'HTML file. Got {path}', path=path))
            return result

        start_files = list(map(create_full_path, self.start_files))

        # Open each files
        for file in start_files:
            opened_file = open(file, mode='r', encoding='utf-8')
            buffer = StringIO(opened_file.read())
            self.buffers.append((file, buffer))
            opened_file.close()

        for path, buffer in self.buffers:
            filename = os.path.basename(path)
            filename, _ = filename.split('.')
            global_logger.logger.info(LazyFormat('Parsing file: {filename}', filename=filename))
            self.start(BeautifulSoup(buffer, 'html.parser'), filename=filename, filepath=path)

    def __del__(self):
        for _, buffer in self.buffers:
            buffer.close()

    @staticmethod
    def _check_path(path: str):
        checks = [
            os.path.isfile(path),
            path.endswith('.html')
        ]
        return all(checks)

    def start(self, soup: BeautifulSoup, **kwargs):
        pass
