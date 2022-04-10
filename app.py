import os
from io import StringIO

from zineb.logger import logger
from zineb.settings import settings
from zineb.utils.formatting import LazyFormat
from zineb.utils.iteration import RequestQueue

DEFAULT_META_OPTIONS = {'domains', 'base_url', 
                        'verbose_name', 'limit_requests_to'}

class SpiderOptions:
    def __init__(self):
        self.options = {}
        self.spider = None
        self.spider_name = None
        self.verbose_name = None
        self.start_urls = []
        self.prepared_requests = None
        
        self.domains = []
        self.base_url = None
        self.limit_requests_to = 0
        
    def __repr__(self):
        return f'<{self.__class__.__name__} for {self.spider.__name__}>'
        
    def update_options(self, cls, name):
        self.spider = cls
        self.spider_name = name.lower()
        self.verbose_name = name
        self.prepared_requests = RequestQueue(*self.start_urls)
        
    def add(self, name, value):
        if name in self.options:
            raise ValueError('Option is already declared')
        
        if name not in DEFAULT_META_OPTIONS:
            raise ValueError('Meta received an illegal option')
        
        if name == 'verbose_name':
            if self.verbose_name is not None:
                self.verbose_name = value            
        
        self.options[name] = value


class BaseSpider(type):
    def __new__(cls, name, bases, attrs):
        create_new = super().__new__
        
        parents = [b for b in bases if not isinstance(b, Spider)]
        if not parents:
            return create_new(cls, name, bases, attrs)
        
        new_class = create_new(cls, name, bases, attrs)
        
        meta = SpiderOptions()
        
        start_urls = attrs.get('start_urls', None)
        meta.start_urls = start_urls
        meta.update_options(new_class, name)
        
        meta_attributes = attrs.pop('Meta', None)
        if meta_attributes is not None:
            attributes_dict = meta_attributes.__dict__
        
            for name, value in attributes_dict.items():
                meta.add(name, value)
                
        setattr(new_class, 'meta', meta)
        return new_class


class Spider(metaclass=BaseSpider):
    """
    To run a spider, you first need to inherit
    from this class. You also need to implement
    a list of starting urls
    """
    start_urls = []

    def __init__(self):
        logger.instance.info(f'Starting {self.__class__.__name__}')
        logger.instance.info(f"{self.__class__.__name__} contains {len(self.meta.prepared_requests)} request(s)")

        # TODO: Send signal when the spider is
        # initialized
            
        self._resolve_requests()

    def __repr__(self):
        return f"{self.__class__.__name__}(requests={len(self.meta.prepared_requests)})"

    def _resolve_requests(self):
        """
        Calls `_send` each requests and passes the response to
        the start method of the same class
        """
        if self.meta.prepared_requests:
            limit_requests_to = self.meta.limit_requests_to
            if limit_requests_to == 0:
                limit_requests_to = len(self.meta.prepared_requests)

            for i, items in enumerate(self.meta.prepared_requests):
                url, request = items
                request._send()

                soup_object = request.html_response.html_page
                self.start(
                    request.html_response,
                    request=request,
                    soup=soup_object
                )

            # TODO: Send a signal after the spider
            # has resolved all the requests

    def start(self, response, request, **kwargs):
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


# class SitemapCrawler(Spider):
#     """
#     Use this class in order to scrap from a
#     websites' sitemaps
#     """


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
            result = os.path.join(settings.PROJECT_PATH, self.root_dir, path)

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
            
        from bs4 import BeautifulSoup
        
        for path, buffer in self.buffers:
            filename = os.path.basename(path)
            filename, _ = filename.split('.')
            logger.logger.info(LazyFormat('Parsing file: {filename}', filename=filename))
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

    def start(self, soup, **kwargs):
        pass


# class MySpider(Spider):
#     start_urls = ['http://example.com']

# spider = MySpider()
# print(spider)
