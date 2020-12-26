from urllib import parse
from urllib.parse import urlparse


class GlobalMixins:
    _default_settings = None
    _errors = []


class RequestsMixins:
    def _check_url_domain_is_valid(self, url):
        parsed_url = urlparse(url)
        valid_domains = [domain for domain in self._default_settings.get('DOMAINS')]
        if parsed_url[1] not in valid_domains:
            pass

class ApplicationChecks(GlobalMixins, RequestsMixins):
    domains = []        

    def __call__(self, sender, signal, **kwargs):
        self._default_settings = kwargs.get('settings', {})
        domains = self._default_settings.get('DOMAINS')
        self.domains = [
            domain for domain in domains
        ]

        name = kwargs.get('name', None)
        if name is not None:
            func = getattr(self, name, None)
            if func is not None:
                func(signal._request.url)

    def _check_settings_valid(self):
        pass

    def _check_domains_validity(self):
        for domain in self.domains:
            if domain.startswith('http') or domain.startswith('www'):
                raise ValueError('Domain should not start with http:// or wwww')
