import hashlib
import hmac
import re
import secrets


def create_new_name(length=5):
    return secrets.token_hex(nbytes=length)


def reconstruct_url(url, pattern=None, func=None):
    if pattern is not None:
        match = re.search(pattern, url)
        if match:
            return match.groups(default=None)
    
    if func is not None:
        return func(url)

    return None


def replace_urls_suffix(urls:list, suffix, replace_with):
    """
    Replace the end part of each url by a string
    
    Parameters
    ----------

        urls (list): lit of urls
        suffix (str): the current suffix
        replace_with (str): the suffix to implement

    Returns:
        [type]: [description]
    """
    replaced_urls = map(lambda url: str(url).removesuffix(suffix), urls)
    return list(map(lambda url: url + replace_with, replaced_urls))
    

def create_secret_key(salt, encoding='utf-8', errors='strict'):
    salt = str(salt).encode(encoding, errors)
    result = str('something').encode(encoding, errors)
    hash_value = hashlib.md5(salt + result).digest()
    hmac_result = hmac.new(hash_value, 'Some message'.encode(encoding, errors), hashlib.sha256)
    return hmac_result.hexdigest()


ALLOWED_CHARACTERS = (
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
)

def random_string(length=15):
    return ''.join(secrets.choice(ALLOWED_CHARACTERS) for _ in range(length))
