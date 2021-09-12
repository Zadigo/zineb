import re


def is_path(path: str):
    # is_match = re.search(r'^(?:[/].*/)(?:.*)$', path)
    is_match = re.search(r'^(?:\/?.*\/?)\??.*$', path)
    if is_match:
        return True
    return False
