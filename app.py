import configparser
import warnings
from collections import deque
from xml.etree import ElementTree

import pandas

from zineb.checks.core import checks_registry
from zineb.exceptions import StartUrlsWarning
from zineb.http.request import HTTPRequest
from zineb.middleware import Middleware
from zineb.settings import Settings
from zineb.signals import post_start, pre_start, signal
from zineb.utils.general import create_logger


class BaseSpider(type):
    settings = Settings()

    def __new__(cls, name, bases, attrs):
        create_new = super().__new__
        if not bases:
            return create_new(cls, name, bases, attrs)

        # if 'Meta' in attrs:
        #     _meta = attrs.pop('Meta')
        #     options = _meta.__dict__

        #     valid_options = OrderedDict()

        #     allowed_options = ['domains']
        #     for key, option in options.items():
        #         if not key.startswith('__'):
        #             if key in allowed_options:
        #                 valid_options.setdefault(key, option)
        #                 attrs.update({'_meta': valid_options})
        #             else:
        #                 raise TypeError(f"Meta received an invalid option: {key}. Authorized options are {', '.join(valid_options)}")

        if name == 'Zineb':
            attrs.setdefault('settings', cls.settings)

            if not 'logger' in attrs:
                params = {
                    'name': name,
                    'debug_level': cls.settings.get('LOG_LEVEL'),
                    'log_format': cls.settings.get('LOG_FORMAT'),
                    'to_file': cls.settings.get('LOG_TO_FILE')
                }
                attrs.update({'logger': create_logger(**params)})
        
        # checks = ApplicationChecks(default_settings=cls.settings)
        # checks.run()

        if 'start_urls' in attrs:
            new_class = create_new(cls, name, bases, attrs)

            start_urls = getattr(new_class, 'start_urls')
            prepared_requests = attrs.get('_prepared_requests', [])
            if start_urls:
                if len(start_urls) > 0:
                    prepared_requests = []
                    for index, link in enumerate(start_urls):
                        request = HTTPRequest(link, counter=index, settings=cls.settings)
                        request.only_secured_requests = cls.settings.get('ENSURE_HTTPS')
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

    def __init__(self, **kwargs):
        self.logger.info(f'Starting {self.__class__.__name__}')

        configuration = configparser.ConfigParser()
        configuration.read(self.settings.get('CONFIGURATION_FILE', 'settings/zineb.conf'))

        self.logger.info(f'Loaded configuration file...')
        self.logger.info(f"{self.__class__.__name__} contains {self.__len__()} request(s)")
        
        middlewares = Middleware()
        middlewares.settings = self.settings
        middlewares._load
        objs = middlewares.loaded_middlewares.values()
        if objs:
            for obj in objs:
                # Each middleware class should provide a 
                # __call__ function that will be called
                # like a regular function by the dispatcher
                receiver = obj()
                # Initialize all the signals and the
                # ones that were created for the project
                signal.connect(receiver, signal=receiver.__class__.__name__, sender=self)

        self._cached_aggregated_results = None
        self._cached_aggregated_results = self._resolve_requests(debug=kwargs.get('debug', False))

    def __len__(self):
        return len(self._prepared_requests)

    def __repr__(self):
        return f"{self.__class__.__name__}(requests={self.__len__()})"

    def _resolve_return_container(self, container):
        from zineb.models.pipeline import Pipe
        if not container or container is None:
            return False

        # callbacks = {item.callback for item in container if item.callback is not None}

        pipe = Pipe(container)
        return pipe._resolve_dataframes()

    def _resolve_requests(self, debug=False):
        """
        Send each requests and pass the response in
        the start method of the class
        """
        if self._prepared_requests:
            if not debug:
                return_values_container = deque()
                for request in self._prepared_requests:
                    request._send()
                    return_value = self.start(request.html_response, request=request)
                    if return_value is not None:
                        return_values_container.append(return_value)

                # post_start.send('History', self)
                # post_start.send('GeneralStatistics', self)
                return self._resolve_return_container(return_values_container)
            else:
                self.logger.warn(f'You are using {self.__class__.__name__} in DEBUG mode')

    def start(self, response, **kwargs):
        """
        Use this function as an entrypoint to scrapping
        your HTML page. This method gets called on the
        initialization of the web spider

        Each response is iterated over and passed through
        this function in addition with the request

        Parameters
        ----------

            response (type): an HTMLResponse object
        """
        pass


class Zineb(Spider):
    """
    This is the base Spider to subclass in order
    to create a scrapping project
    """
    start_urls = []


class SitemapCrawler(Spider):
    pass
