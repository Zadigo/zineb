from zineb.checks.core import checks_registry
from w3lib.url import urlparse

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


E001 = ('Proxy should be a tuple or list containing the proxy '
        'type and the IP address e.g. (http, 127.0.0.1)')

E002 = ('Could not recognize the scheme in proxy: {proxy}. Should be one of http or https')


E003 = ('IP address in proxy cannot be empty')


E004 = ("Middleware should be string pointing to a module in your project")


E005 = ('DEFAULT_REQUEST_HEADERS should be a dictionnary')


@checks_registry.register(tag='middlewares')
def check_middlewares(project_settings):
    errors = []
    middlewares = project_settings.get('MIDDLEWARES', None)
    if middlewares is None:
        return [W001]

    if middlewares == []:
        return []

    for middleware in middlewares:
        if not isinstance(middleware, str):
            errors.append(E004)
    return errors


@checks_registry.register(tag='headers')
def check_default_request_headers(project_settings):
    default_request_headers = project_settings.get('DEFAULT_REQUEST_HEADERS', False)
    if not isinstance(default_request_headers, dict):
        return [E005]
    return [] if not default_request_headers else []


@checks_registry.register(tag='proxies')
def check_proxies_valid(project_settings):
    errors = []
    proxies = project_settings.get('PROXIES')
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
    return errors


def D001(parsed_domain, domain):
    return ('Domains in DOMAINS should not start with '
        f'http:// or wwww. Use {parsed_domain[1]} instead of {domain}')


@checks_registry.register(tag='domains')
def check_domains_validity(project_settings):
    errors = []
    domains = project_settings.get('DOMAINS')
    for domain in domains:
        if domain.startswith('http') or domain.startswith('www'):
            parsed_domain = urlparse(domain)
            errors.append(D001(parsed_domain, domain))
    return errors
