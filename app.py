import configparser
from collections import OrderedDict

from zineb.http.request import HTTPRequest
from zineb.middleware import Middleware
from zineb.settings import Settings
from zineb.signals import post_start, pre_start, signal
from zineb.utils.general import create_logger


class BaseSpider(type):
    def __new__(cls, name, bases, attrs):
        new_class = super().__new__(cls, name, bases, attrs)

        if hasattr(new_class, 'start_urls'):
            logger = getattr(new_class, 'logger', None)
            if logger is None:
                logger = create_logger(name)
                setattr(new_class, 'logger', logger)

            prepared_requests = getattr(new_class, 'prepared_requests', [])
            if not prepared_requests:
                links = getattr(new_class, 'start_urls', [])
                cls._create_initial_requests(new_class, links)
                # cls.http_requests_store.update({name: new_class.prepared_requests.copy()})

            if hasattr(new_class, 'Meta'):
                _meta = getattr(new_class, 'Meta')
                options = _meta.__dict__

                allowed_options = ['ordering', 'options', 'restrict_to_domain']
                valid_options = OrderedDict()
                for key, option in options.items():
                    if key in allowed_options:
                        valid_options.setdefault(key, option)
                        setattr(new_class, '_meta', valid_options)
                    # else:
                    #     raise AttributeError(f"Attribute Meta only allows the following options: {', '.join(allowed_options)}")

            # Collect all the parser methods
            # from the newly created classes
            # in order to be executed later on
            # parse_function = getattr(new_class, 'parse')
            # if parse_function is not None:
            #     cls.parse_functions_store.setdefault(name, parse_function)
        return new_class

    @classmethod
    def _create_initial_requests(cls, new_class, links):
        if len(links) > 0:
            prepared_requests = []
            # prepared_requests = getattr(new_class, 'prepared_requests', [])
            for index, link in enumerate(links):
                prepared_requests.append(HTTPRequest(link, cursor=index))
            setattr(new_class, 'prepared_requests', prepared_requests)
    
    @classmethod
    def _execute_parsers(cls, new_class, parsers):
        pass


class Zineb(metaclass=BaseSpider):
    """
    To run a spider with Zineb, you need to inherit
    from this class and implement a list of starting
    urls to scrap

    Parameters
    ----------

        confifuration (dict, optional): A set of default values to use. Defaults to None
    """
    start_urls = []
    prepared_requests = []
    connected_signals = []

    def __init__(self, configuration=None):
        self.logger.info('Starting Zineb')

        self.settings = Settings()

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
                signal.connect(receiver, receiver.__class__.__name__)

        # Initialize all the signals and the
        # ones that were created for the project
        # pre_start.connect('', self)

        if self.prepared_requests:
            for request in self.prepared_requests:
                request._send()

        # Now finally call the base start()
        # function of the class in order to
        # start the parsing
        # for resolved_request in self.prepared_requests:
        #     self.start(resolved_request)

        # post_start.connect('Function that receives', self, self.prepared_requests)

    def __len__(self):
        return len(self.prepared_requests)

    def __repr__(self):
        return f"{self.__class__.__name__}(requests={self.__len__()})"

    def get_response(self, index):
        try:
            return self.prepared_requests[index]
        except IndexError:
            self.logger.error('There are a no requests to be used')

    def start(self, response, **kwargs):
        return response, kwargs


class SitemapCrawler(Zineb):
    def __iter__(self):
        pass
