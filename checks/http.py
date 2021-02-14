# class RequestsMixins:
#     def _check_url_domain_is_valid(self, url):
#         parsed_url = urlparse(url)
#         valid_domains = [
#             domain for domain in self._default_settings.get('DOMAINS')]
#         if parsed_url[1] not in valid_domains:
#             pass


from zineb.checks.core import checks_registry

@checks_registry.register(tag='domain')
def check_url_domain_is_valid(project_settings):
    valid_domaines = project_settings.get('DOMAINS', [])
