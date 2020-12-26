import configparser
import warnings
from collections import OrderedDict
from xml.etree import ElementTree

import settings
from zineb.http.request import HTTPRequest
from zineb.middleware import Middleware
from zineb.settings import Settings
from zineb.signals import post_start, pre_start, signal
from zineb.utils.general import create_logger


class BaseSpider(type):
    def __new__(cls, name, bases, attrs):
        create_new = super().__new__
        if 'start_urls' in attrs:
            if not 'logger' in attrs:
                attrs.update({'logger': create_logger(name)})

            if 'Meta' in attrs:
                _meta = attrs.pop('Meta')
                options = _meta.__dict__

                valid_options = OrderedDict()

                allowed_options = ['domains']
                for key, option in options.items():
                    if not key.startswith('__'):
                        if key in allowed_options:
                            valid_options.setdefault(key, option)
                            attrs.update({'_meta': valid_options})
                        else:
                            raise TypeError(f"Meta received an invalid option: {key}. Authorized options are {', '.join(valid_options)}")

            new_class = create_new(cls, name, bases, attrs)

            prepared_requests = attrs.get('_prepared_requests', [])
            if not prepared_requests:
                start_urls = getattr(new_class, 'start_urls')
                if not start_urls:
                    warnings.warn('No starting URLs were specified for you project')
                else:
                    cls._create_initial_requests(new_class, start_urls)
            return new_class
        return create_new(cls, name, bases, attrs)

    @classmethod
    def _create_initial_requests(cls, new_class, links):
        if len(links) > 0:
            prepared_requests = []
            for index, link in enumerate(links):
                prepared_requests.append(HTTPRequest(link, counter=index))
            setattr(new_class, '_prepared_requests', prepared_requests)


class Zineb(metaclass=BaseSpider):
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
    start_urls = []
    _prepared_requests = []

    def __init__(self, configuration=None, **kwargs):
        self.logger.info('Starting Zineb')

        self.settings = Settings()
        restricted_domains = self.settings.get('DOMAINS')

        configuration = configparser.ConfigParser()
        configuration.read(self.settings.get('CONFIGURATION_FILE', 'project.conf'))

        self.logger.info('Loaded configuration file...')
        self.logger.info(
            f'{self.__class__.__name__} contains {self.__len__()} requests'
        )
        
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
                signal.connect(receiver, receiver.__class__.__name__)

        signal.send('ApplicationChecks', self, settings=self.settings)
        self._resolve_requests(debug=kwargs.get('debug', False))

        # post_start.send('History', self)

    def __len__(self):
        return len(self._prepared_requests)

    def __repr__(self):
        return f"{self.__class__.__name__}(requests={self.__len__()})"

    def _resolve_requests(self, debug=False):
        """
        Send each requests and pass the response in
        the start method of the class
        """
        if self._prepared_requests:
            # pre_start.send('History', self)
            if not debug:
                for request in self._prepared_requests:
                    request._send()
                    self.start(request.html_response, request=request)
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


class SitemapCrawler(Zineb):
    def _resolve_requests(self):
        if self._prepared_requests:
            pre_start.send('History', self)
            for request in self._prepared_requests:
                request._send()
