import re
from urllib.parse import urlparse

from zineb.checks.core import checks_registry

E001 = (
    "This domain is not a valid form : {domain}. A domain should look "
    "like example.com or myexample.com"
)

E002 = (
    "Retry codes should be integers. Got {retry_code}."
)

E003 = (
    "User agent should be of type string. Got {user_agent}."
)

E004 = ('RANDOMIZE_USER_AGENTS should be a boolean')



def D001(parsed_domain, domain):
    return ("Domains in DOMAINS should not start with "
            f"http:// or wwww. Use {parsed_domain[1]} instead of {domain}")


@checks_registry.register(tag='domains')
def check_domains_validity(project_settings):
    errors = []
    domains = project_settings.get('DOMAINS')
    for domain in domains:
        if domain.startswith('http') or domain.startswith('www'):
            parsed_domain = urlparse(domain)
            errors.append(D001(parsed_domain, domain))
    return errors


@checks_registry.register(tag='domain_url')
def check_domain_url(project_settings):
    errors = []
    valid_domains = project_settings.get('DOMAINS', [])
    for domain in valid_domains:
        is_match = re.match(r'^.*(?:\.\w+)', domain)
        if not is_match:
            errors.append(E001.format(domain=domain))
    return errors


@checks_registry.register(tag='retry_codes')
def check_retry_http_codes(project_settings):
    errors = []
    retry_codes = project_settings.get('RETRY_HTTP_CODES')
    for retry_code in retry_codes:
        if not isinstance(retry_code, int):
            errors.append(E002.format(retry_code))
    return errors


def check_user_agent(project_settings):
    errors = []
    user_agents = project_settings.get('USER_AGENTS')
    for agent in user_agents:
        if not isinstance(agent, str):
            errors.append([E003])
    return errors


@checks_registry.register(tag='randomize_user_agents')
def check_randomize_user_agent(project_settings):
    result = project_settings.get('RANDOMIZE_USER_AGENTS')
    if not isinstance(result, bool):
        return [E004]
