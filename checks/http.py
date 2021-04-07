from zineb.checks.core import checks_registry

@checks_registry.register(tag='domain')
def check_url_domain_is_valid(project_settings):
    valid_domaines = project_settings.get('DOMAINS', [])
