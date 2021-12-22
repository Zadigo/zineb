import re
from datetime import timezone

from zineb.checks.core import register
from zineb.settings import settings

W001 = Warning(
    "You do not have zineb.middlewares in your settings"
)


W002 = Warning(
    "You do not have zineb.middleware in our settings"
)


W003 = Warning(
    "Retries should not exceed"
    # id='security.W003'
)


W004 = Warning(
    'Timezone is not implemented in your project'
)


E001 = ('Proxy should be a tuple or a list type containing the scheme and the IP/url address e.g. (http, 127.0.0.1)')


E002 = ('Could not recognize the scheme in proxy: {proxy}. Should be one of http or https')


E003 = ('IP address in proxy cannot be empty')


E004 = ("Middleware should be string pointing to a module in your project. Got '{middleware}'")


E005 = ('DEFAULT_REQUEST_HEADERS should be a dictionnary')


E006 = ('IP address in PROXIES is not valid. Got {proxy}.')


E007 = ('MEDIA_FOLDER should either be None or a string representing a relative or absolute path')


E008 = ('TIME_ZONE should be a string. Got {timezone}')


@register(tag='middlewares')
def check_middlewares():
    errors = []
    middlewares = settings.get('MIDDLEWARES', None)
    if middlewares is None:
        return [W001]

    if middlewares == []:
        return []

    for middleware in middlewares:
        if not isinstance(middleware, str):
            errors.append(E004.format(middleware=middleware))
    return errors


@register(tag='headers')
def check_default_request_headers():
    default_request_headers = settings.get('DEFAULT_REQUEST_HEADERS', False)
    if not isinstance(default_request_headers, dict):
        return [E005]
    return [] if not default_request_headers else []


@register(tag='proxies')
def check_proxies_valid():
    errors = []
    proxies = settings.get('PROXIES')
    if proxies is None:
        return [E001]

    regexes = [
        # 1.1.1.1
        r'^[\d+\d.]+$',
        # http://1.1.1.1:8080
        r'^https?\:\/\/[d+\d.]+\:?\d+$',
        # http://user:pass@1.1.1.1:8080
        r'^https?\:\/\/([a-zA-Z0-9]+)\:([a-zA-Z0-9]+)\@[\d+\.]+\:\d+$'
    ]

    for proxy in proxies:
        if not isinstance(proxy, (tuple, list)):
            errors.append(E001)
        else:
            proxy_type, ip = proxy

            allowed_schemes = ['http', 'https']
            if (proxy_type == '' or
                    proxy_type is None or
                        proxy_type not in allowed_schemes):
                errors.append(E002.format(proxy=proxy))

            if ip == '' or ip is None:
                errors.append(E003)

            matched_regex = []

            for regex in regexes:
                is_match = re.match(regex, ip)
                if not is_match:
                    matched_regex.append(False)
                else:
                    matched_regex.append(True)

            if not any(matched_regex):
                errors.append(E006.format(proxy=proxy))

    return errors


@register(tag='media_folder')
def check_media_folder():
    media_folder = settings.MEDIA_FOLDER
    if media_folder is not None and not isinstance(media_folder, str):
        return [E007]
    

@register(tag='timezone')
def check_test_timzone():
    if settings.TIME_ZONE is None:
        return []

    if not isinstance(settings.TIME_ZONE, str):
        return [E008.format(timezone=settings.TIME_ZONE)]
