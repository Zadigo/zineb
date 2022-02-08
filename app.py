import os
import warnings
from collections import OrderedDict
from io import StringIO
from typing import Union

from bs4 import BeautifulSoup

from zineb import global_logger, signals
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse, JsonResponse, XMLResponse
from zineb.settings import settings as global_settings
from zineb.utils.formatting import LazyFormat
from zineb.utils.iteration import RequestQueue, drop_while


class SpiderOptions:
    allowed_options = ['domains', 'base_url', 'verbose_name', 'limit_requests_to']
    
    def __init__(self):
        self.spider_name = None
        self.python_path = None
        defaults = {
            'domains': [],
            'base_url': None,
            'verbose_name': None,
            'limit_requests_to': 0
        }
        self.options = OrderedDict(defaults)
        
    def __repr__(self):
        return f"{self.__class__.__name__}(spider={self.get_option_by_name('verbose_name')})"
    
    def __getitem__(self, name):
        return self.options[name]
            
    def _check_options(self, options):
        requires_list_or_tuple = ['domains', 'sorting']
        
        for key, value in options.items():
            if key not in self.allowed_options:
                raise ValueError(LazyFormat('Meta in spider {spider} received an illegal option: {option}', spider=self.spider_name, option=key))
            
            if key in requires_list_or_tuple:
                if not isinstance(value, (list, tuple)):
                    raise TypeError('Domains should be etc')
                
                for item in value:
                    if not isinstance(item, str):
                        raise TypeError('Domain should be a string')
            else:
                if not isinstance(value, (str, int)):
                    raise TypeError('Value should be a string')
            
    def has_option(self, name):
        return name in self.options
    
    def get_option_by_name(self, name):
        return self.options[name]
    
    def update(self, options):
        self._check_options(options)
        self.options.update(options)


class BaseSpider(type):
    def __new__(cls, name, bases, attrs):
        create_new = super().__new__
        if not bases:
            return create_new(cls, name, bases, attrs)
                
        meta = SpiderOptions()
        if 'Meta' in attrs:
            _meta = attrs.pop('Meta')
            _meta_dict = _meta.__dict__
            
            default_options = {}
            cleaned_options = drop_while(lambda x: x[0].startswith('__'), _meta_dict.items())
            cleaned_options = OrderedDict(list(cleaned_options))
            default_options.update(cleaned_options)
            
            verbose_name = _meta_dict.get('verbose_name')
            if verbose_name is None:
                default_options['verbose_name'] = name
            meta.spider_name = default_options['verbose_name']
                        
            meta.update(default_options)
            meta.python_path = f"spiders.{name}"
            
        attrs['_meta'] = meta
        
        new_class = create_new(cls, name, bases, attrs)
        
        start_urls = []
        if 'start_urls' in attrs:            
            start_urls = getattr(new_class, 'start_urls')
            if not start_urls:
                warnings.warn("No start urls were provided for the spider", Warning, stacklevel=0)
            
        instance = RequestQueue(*start_urls)
        setattr(new_class, '_prepared_requests', instance)
        return new_class


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
    """
    # _prepared_requests = []
    start_urls = []

    def __init__(self, **kwargs):
        global_logger.info(f'Starting {self.__class__.__name__}')
        global_logger.info(f"{self.__class__.__name__} contains {len(self._prepared_requests)} request(s)")

        # TODO:
        # signal.send(dispatcher.Any, self, tag='Pre.Start')
            
        self._cached_aggregated_results = None
        self._cached_aggregated_results = self._resolve_requests(debug=kwargs.get('debug', False))

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
        Calls `_send` each requests and passes the response to
        the start method of the same class
        """
        if self._prepared_requests:
            if not debug:
                limit_requests_to = self._meta.get_option_by_name('limit_requests_to')
                if limit_requests_to == 0:
                    limit_requests_to = len(self._prepared_requests)

                for i, items in enumerate(self._prepared_requests):
                    url, request = items
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
    
    def __repr__(self):
        return f"{self.__class__.__name__}(requests={len(self._prepared_requests)})"



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
        # default to the default 'media' folder
        if self.root_dir is None:
            self.root_dir = 'media'

        def create_full_path(path):
            result = os.path.join(global_settings.PROJECT_PATH, self.root_dir, path)

            if not os.path.isfile(result):
                raise ValueError(LazyFormat('Path does not point to a valid HTML file. Got {path}', path=path))
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
