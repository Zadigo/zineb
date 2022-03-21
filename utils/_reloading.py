from collections import namedtuple
from urllib.parse import urlparse, quote
import string
import threading
import logging
import time

logger = logging.getLogger('Reloader')



class ReloaderError(Exception):
    pass


class BaseReloader:
    SLEEPING_TIME = 1

    def __init__(self):
        self._stop_condition = threading.Event()

    @property
    def should_stop(self):
        # The flag is set to False all time
        # there is not indication that that
        # the thread should stop
        return self._stop_condition.is_set()

    def stop(self):
        return self._stop_condition.set()

    def loop(self):
        events = self.events()

    def events(self):
        while True:
            time.sleep(self.SLEEPING_TIME)
            yield

    def run(self, main_thread):
        logging.debug('Autoreload started')
        self.loop()



class StatReloader(BaseReloader):
    pass


def start_server(reloader, func, *args, **kwargs):
    main_thread = threading.Thread(target=func, args=args, kwargs=kwargs, name='zineb-thread')
    main_thread.setDaemon(True)
    main_thread.start()

    while not reloader.should_stop:
        try:
            reloader.run(main_thread)
        except ReloaderError:
            logger.debug('Some error')

def some_function():
    pass


start_server(StatReloader(), some_function)


# from w3lib.url import canonicalize_url


RFC3986_GEN_DELIMS = b':/?#[]@'

RFC3986_SUB_DELIMS = b"!$&'()*+,;="

RFC3986_RESERVED = RFC3986_GEN_DELIMS + RFC3986_SUB_DELIMS

RFC3986_UNRESERVED = (string.ascii_letters +
                      string.digits + "-._~").encode('ascii')

EXTRA_SAFE_CHARS = b'|'

SAFE_CHARACTERS = RFC3986_RESERVED + RFC3986_UNRESERVED + EXTRA_SAFE_CHARS + b'%'


def convert_to_unicode(text: bytes, encoding: str = 'utf-8', errors: str = 'strict'):
    if isinstance(text, str):
        return text
    if not isinstance(text, bytes):
        raise TypeError('Text should be bytes')
    return text.decode(encoding, errors)


def convert_to_bytes(text: str, encoding: str = 'utf-8', errors: str = 'strict'):
    if isinstance(text, bytes):
        return text
    return text.encode(encoding, errors)


def render_safe(url_parts, encoding='utf-8', path_encoding='utf-8'):
    netloc = None
    # 'path', 'params', 'query', 'fragment'
    instance = namedtuple(
        'url', ['scheme', 'netloc', 'path', 'params', 'query', 'fragment'])
    return instance(
        convert_to_unicode(url_parts.scheme),
        convert_to_unicode(url_parts.netloc),
        quote(convert_to_unicode(url_parts.path, encoding), SAFE_CHARACTERS),
        quote(convert_to_unicode(url_parts.params, encoding), SAFE_CHARACTERS),
        quote(convert_to_unicode(url_parts.query, encoding), SAFE_CHARACTERS),
        quote(convert_to_unicode(url_parts.fragment, encoding), SAFE_CHARACTERS),
    )


def canonicalize_url(url, encoding='utf-8'):
    parsed_url = urlparse(url)
    items = render_safe(parsed_url, encoding=encoding)
    query = parse_qsl(parsed_url.query)
    query.sort()
    query = urlencode(query)
    return urlunparse((items.scheme, items.netloc, items.path, items.params, items.query, items.fragment))


print(canonicalize_url('http://example.com/google/1?fast=true&taste=1'))
# def _safe_ParseResult(parts, encoding='utf8', path_encoding='utf8'):
#     # IDNA encoding can fail for too long labels (>63 characters)
#     # or missing labels (e.g. http://.example.com)
#     try:
#         netloc = parts.netloc.encode('idna')
#     except UnicodeError:
#         netloc = parts.netloc

#     return (
#         to_native_str(parts.scheme),
#         to_native_str(netloc),

#         # default encoding for path component SHOULD be UTF-8
#         quote(to_bytes(parts.path, path_encoding), _safe_chars),
#         quote(to_bytes(parts.params, path_encoding), _safe_chars),

#         # encoding of query and fragment follows page encoding
#         # or form-charset (if known and passed)
#         quote(to_bytes(parts.query, encoding), _safe_chars),
#         quote(to_bytes(parts.fragment, encoding), _safe_chars)
# )
# def canonicalize_url(url, keep_blank_values=True, keep_fragments=False, encoding=None):
#     try:
#         scheme, netloc, path, params, query, fragment = _safe_ParseResult(
#             parse_url(url), encoding=encoding)
#     except UnicodeEncodeError as e:
#         scheme, netloc, path, params, query, fragment = _safe_ParseResult(
#             parse_url(url), encoding='utf8')
#     if six.PY2:
#         keyvals = parse_qsl(query, keep_blank_values)
#     else:
#     keyvals.sort()
#     query = urlencode(keyvals)
#     path = quote(uqp, _safe_chars) or '/'

#     fragment = '' if not keep_fragments else fragment

#     # every part should be safe already
#     return urlunparse((scheme,
#                        netloc.lower().rstrip(':'),
#                        path,
#                        params,
#                        query,
#                        fragment))
