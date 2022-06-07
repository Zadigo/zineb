import re
from urllib.parse import urlparse

from zineb.checks.core import register
from zineb.settings import settings

E001 = (
    "This domain is not a valid form : {domain}. A domain should look "
    "like example.com or myexample.com"
)


E002 = ("Retry codes should be integers. Got {retry_code}.")


E003 = ("User agent should be of type string. Got {user_agent}.")


E004 = ('{setting_name} should be a boolean')



def D001(parsed_domain, domain):
    return ("Domains in DOMAINS should not start with "
            f"http:// or wwww. Use {parsed_domain[1]} instead of {domain}")


@register(tag='domains')
def check_domains_validity():
    errors = []
    for domain in settings.DOMAINS:
        if domain.startswith('http') or domain.startswith('www'):
            parsed_domain = urlparse(domain)
            errors.append(D001(parsed_domain, domain))
    return errors


@register(tag='domain_url')
def check_domain_url():
    errors = []
    for domain in settings.DOMAINS:
        is_match = re.match(r'^.*(?:\.\w+)', domain)
        if not is_match:
            errors.append(E001.format(domain=domain))
    return errors


@register(tag='retry_codes')
def check_retry_http_codes():
    errors = []
    for retry_code in settings.RETRY_HTTP_CODES:
        if not isinstance(retry_code, int):
            errors.append(E002.format(retry_code))
    return errors


@register(tag='user_agents')
def check_user_agent():
    errors = []
    for agent in settings.USER_AGENTS:
        if not isinstance(agent, str):
            errors.append([E003])
    return errors


@register(tag='randomize_user_agents')
def check_randomize_user_agent():
    if not isinstance(settings.RANDOMIZE_USER_AGENTS, bool):
        return [E004.format(setting_name='RANDOMIZE_USER_AGENTS')]
    
    
@register(tag='ensure_https')
def check_randomize_user_agent():
    if not isinstance(settings.ENSURE_HTTPS, bool):
        return [E004.format(setting_name='ENSURE_HTTPS')]
