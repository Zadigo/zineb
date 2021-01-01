from zineb.checks.core import checks_registry
from w3lib.url import urlparse

W001 = Warning(
    "You do not have zineb.middlewares in your settings"
)

W002 = Warning(
    "You do not have zineb.middleware in our settings"
)


W003 = Warning(
    "Retries should not exceed",
    id='security.W003'
)


E001 = ('Proxy should be a tuple or list containing the proxy'
        'type and the IP address e.g. (http, 127.0.0.1)')

E002 = ('Could not recognize proxy type. Should be one of http or https')


E003 = ('IP address cannot be empty')


@checks_registry.register(tag=None)
def check_middlewares(project_settings):
    return [] if False else [W001]


@checks_registry.register(tag=None)
def check_retries(project_settings):
    return [] if False else [W002]


@checks_registry.register(tag=None)
def check_proxies_valid(project_settings):
    errors = []
    proxies = project_settings.get('PROXIES')
    for proxy in proxies:
        if not isinstance(proxy, (tuple, list)):
            errors.append(E001)

        proxy_type, ip = proxy

        if proxy_type == '' or proxy_type is None:
            errors.append(E002)

        if ip == '' or ip is None:
            raise errors.append(E003)
    return errors


def D001(parsed_domain, domain):
    return (f'Domains in DOMAINS should not start with'
        f'http:// or wwww. Use {parsed_domain[1]} instead of {domain}')


@checks_registry.register(tag=None)
def check_domains_validity(project_settings):
    errors = []
    domains = project_settings._default_settings.get('DOMAINS')
    for domain in domains:
        if domain.startswith('http') or domain.startswith('www'):
            parsed_domain = urlparse(domain)
            errors.append(D001(parsed_domain, domain))
    return errors
