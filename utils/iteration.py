import os
import re
from collections import defaultdict
from functools import lru_cache
from typing import Callable, Iterable, OrderedDict, Union
from urllib.parse import urlparse

from zineb import exceptions
from zineb.utils.formatting import LazyFormat


def keep_while(func: Callable, values: Iterable):
    """
    A custom keep_while function that does not stop
    on False but completes all the list

    Parameters
    ----------

        func (Callable): [description]
        values (Iterable): [description]

    Yields
    ------

        Any: value to return
    """
    for value in values:
        result = func(value)
        if result:
            yield value


def drop_while(func: Callable, values: Iterable):
    """
    A custom drop_while function that does not stop
    on True but completes all the list

    Parameters
    ----------

        func (Callable): [description]
        values (Iterable): [description]

    Yields
    ------
    
        Any: value to return
    """
    for value in values:
        result = func(value)
        if not result:
            yield value


def split_while(func: Callable, values: Iterable):
    """
    Splits a set of values in seperate lists
    depending on whether the result of the function
    return True or False

    Parameters
    ----------

        func (Callable): [description]
        values (Iterable): [description]

    Returns
    -------

        tuple: ([true values], [false values])
    """
    a = [value for value in values if func(value)]
    b = [value for value in values if not func(value)]
    return a, b


@lru_cache(maxsize=0)
def collect_files(dir_name: str, func: Callable = None):
    """
    Collect all the files within specific
    directory of your project. This utility function
    is very useful with the FileCrawler:

        class Spider(FileCrawler):
            start_files = collect_files('some/path')

    Parameters
    ----------

        - path (str): relative path to the directory
        - func (Callable): a func that can be used to filter the files
    """
    from zineb.settings import settings
    
    if settings.PROJECT_PATH is None:
        raise exceptions.ProjectNotConfiguredError()

    full_path = os.path.join(settings.PROJECT_PATH, dir_name)
    if not os.path.isdir(full_path):
        raise ValueError(LazyFormat("Path should be a directory. Got '{path}'", path=full_path))

    root, _, files = list(os.walk(full_path))[0]
    if full_path:
        files = map(lambda x: os.path.join(root, x), files)

    if func is not None:
        return filter(func, files)

    return files


def regex_iterator(text: str, regexes: Union[tuple, list]):
    """
    Check a text string against a set of regex values

    Parameters
    ----------

        - text (str): a string to test
        - regexes (Union[tuple, list]): a tuple/list of regexes
    """
    result = None
    for regex in regexes:
        result = re.search(regex, text)
        if result:
            result = result.groups()
    return result


class RequestQueue:
    """Class that stores and manages all the
    starting urls of a given spider"""

    request_queue = OrderedDict()
    history = defaultdict(dict)

    def __init__(self, *urls, **request_params):
        self.spider = None
        self.domain_constraints = []
        self.request_params = request_params
        self.url_strings = list(urls)
        self.retry_policies = {}
        
    def __repr__(self):
        return f"<{self.__class__.__name__}(urls={len(self.request_queue)})>"

    def __iter__(self):
        from zineb.logger import logger
        for url, request in self.request_queue.items():
            try:
                if not self.is_valid_domain(url):
                    logger.instance.info(f"Skipping url '{url}' because it violates constraints on domain")
                    continue
                
                request._send()
            except:
                self.history[url].update({'failed': True, 'request': request})
            else:
                
                
                self.history[url].update({'failed': False, 'request': request})
            yield url, request

    def __len__(self):
        return len(self.request_queue)

    def __enter__(self, *args, **kwargs):
        return self.request_queue

    def __exit__(self, *args, **kwargs):
        return False

    def __getitem__(self, url):
        return self.request_queue[url]

    def __delitem__(self, url):
        return self.request_queue.pop(url)

    def __contains__(self, url):
        return url in self.urls

    def __add__(self, instance):
        if not isinstance(instance, RequestQueue):
            raise TypeError('Instance should be an instance of RequestQueue')
        
        self_urls = self.urls
        self_urls.extend(instance.urls)
        return RequestQueue(self.spider, *self_urls)

    @property
    def has_urls(self):
        return len(self.urls) > 0

    @property
    def requests(self):
        return list(self.request_queue.items())

    @property
    def urls(self):
        return list(self.request_queue.keys())

    @property
    def failed_requests(self):
        return keep_while(lambda x: x['failed'], self.history.items())

    def _retry(self):
        successful_retries = set()
        for url, instance in self.failed_requests:
            if self._zineb_settings.RETRY:
                for i in range(self._zineb_settings.RETRIES):
                    if instance.request.status_code in self._zineb_settings.RETRY_CODES:
                        instance._send()
                        if instance.request.status_code == 200:
                            successful_retries.add(instance)
        return successful_retries
        
    def prepare(self, spider):
        from zineb.http.request import HTTPRequest
        from zineb.settings import settings
        self.spider = spider
        self.domain_constraints = spider.meta.domains
        for i, url in enumerate(self.url_strings):
            self.request_queue[url] = HTTPRequest(
                url, counter=i, **self.request_params
            )
            
        settings_values = ['RETRY', 'RETRY_TIMES', 'RETRY_HTTP_CODES']
        for value in settings_values:
            self.retry_policies[value] = getattr(settings, value)

    def checks(self):
        errors = []
        for url in self.url_strings:
            if not isinstance(url, str):
                errors.extend([])

    def get(self, url, parsed=False):
        if parsed:
            return urlparse(url)
        return self.request_queue[url]

    def has_url(self, url):
        return url in self.request_queue.keys()

    def compare(self, url, url_to_compare):
        result = self.get(url_to_compare, parsed=True)
        url = urlparse(url)
        return result.netloc == url.netloc
    
    def is_valid_domain(self, url):
        url = self.get(url, parsed=True)
        if self.domain_constraints:
            return url.netloc in self.domain_constraints
        return True
