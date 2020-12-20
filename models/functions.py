from zineb.utils.html import deep_clean

def concatenate(a, b):
    if isinstance(a, str):
        a = deep_clean(a)
    if isinstance(b, str):
        b = deep_clean(b)
    return ' '.join([a, b])
