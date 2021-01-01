class RequestsMixins:
    def _check_url_domain_is_valid(self, url):
        parsed_url = urlparse(url)
        valid_domains = [
            domain for domain in self._default_settings.get('DOMAINS')]
        if parsed_url[1] not in valid_domains:
            pass
