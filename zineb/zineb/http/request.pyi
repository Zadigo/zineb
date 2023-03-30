from typing import (Callable, Dict, Generator, Generic, List, Literal,
                    Optional, OrderedDict, TypeVar, Union)
from urllib.parse import ParseResult

from requests.models import Request, Response

from zineb.http.responses import HTMLResponse
from zineb.tags import ImageTag, Link

T = TypeVar('T', object, covariant=True)

class BaseRequest(Generic[T]):
    can_be_sent: bool = ...
    domain: str = ...
    errors: list = ...
    http_methods: List[Literal['GET', 'POST']] = ...
    only_secured_requests: bool = ...
    only_domains: list = ...
    only_secured_requests: bool = ...
    resolved: bool = ...
    root_url: str = ...
    url: bytes = ...
    _url_meta: ParseResult = ...
    _http_response: Request = ...
    _proxy: dict = ...
    def __init__(
        self,
        url: Union[str, Link, ImageTag], 
        method: Optional[Literal['GET']] = ..., 
        **kwargs
    ) -> None: ...
    def __repr__(self) -> str: ...
    @classmethod
    def follow(cls, url: str) -> Response: ...
    @classmethod
    def follow_all(
        cls,
        urls: Union[List[str, Link], List[str, str]]
    ) -> Generator: ...
    def _send(self) -> Response: ...


class HTTPRequest(BaseRequest):
    counter: int = ...
    html_response: HTMLResponse = ...
    options: OrderedDict = ...
    referer: str = ...
    _http_response: Response = ...
    def __init__(
        self, url: str,
        is_download_url: bool = ..., 
        **kwargs
    ) -> None: ...
    def _send(self) -> None: ...
    def urljoin(
        self,
        path: str,
        use_domain: bool = ...
    ) -> str: ...
    def json(
        self,
        sort_by: str = None, 
        filter_func: Callable = None
    ) -> Union[List, Dict]: ...
    
    
# class FormRequest(BaseRequest):
#     fields: list = ...
#     def __init__(self, url: Union[Link, str], data: dict, method: str = 'POST', **attrs) -> None: ...
