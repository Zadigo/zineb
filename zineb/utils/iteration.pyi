from email.generator import Generator
import os
import re
from collections import defaultdict
from functools import lru_cache
from typing import Callable, Iterable, OrderedDict, Union, Optional 
from urllib.parse import ParseResult

from zineb.app import Spider


def keep_while(func: Callable, values: Iterable) -> Generator: ...


def drop_while(func: Callable, values: Iterable) -> Generator: ...


def split_while(func: Callable, values: Iterable) -> tuple: ...


@lru_cache(maxsize=0)
def collect_files(dir_name: str, func: Callable = None) -> Union[filter, list[str], map]: ...


def regex_iterator(text: str, regexes: Union[tuple, list]) -> tuple[str]: ...


class RequestQueue:
    domain_constraints: list = ...
    history: defaultdict(dict) = ...
    request_queue: OrderedDict() = ...
    request_params: dict = ...
    retry_policies: dict = ...
    spider: Spider = ...
    url_strings: list[str] = ...
    def __init__(self, *urls: tuple[str], **request_params) -> None: ...
    def __repr__(self) -> str: ...
    def __iter__(self) -> Generator: ...
    def __len__(self) -> int: ...
    def __enter__(self, *args, **kwargs) -> RequestQueue: ...
    def __exit__(self, *args, **kwargs) -> bool: ...
    def __getitem__(self, url: str) -> str: ...
    def __delitem__(self, url: str) -> str: ...
    def __contains__(self, url: str) -> bool: ...
    def __add__(self, instance: RequestQueue) -> RequestQueue: ...
    @property
    def has_urls(self) -> bool: ...
    @property
    def requests(self) -> list: ...
    @property
    def urls(self) -> list: ...
    @property
    def failed_requests(self) -> Generator: ...
    def _retry(self) -> set: ...
    def prepare(self, spider: Spider) -> None: ...
    def checks(self) -> None: ...
    def get(self, url: str, parsed = Optional[bool]) -> Union[str, ParseResult]: ...
    def has_url(self, url: str) -> bool: ...
    def compare(self, url: str, url_to_compare: str) -> bool: ...
    def is_valid_domain(self, url: str) -> bool: ...
