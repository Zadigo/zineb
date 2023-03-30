class LazyFormat:
    """
    Lazily formats a string until it is called or required 
    to be used

    Example
    -------

    >>> message = LazyFormat('Kendall {name}', name='Jenner')
    ... str(message)
    ... Kendall Jenner
    """
    
    __slots__ = ('_cached_result', '_string_to_format', '_args', '_kwargs')

    def __init__(self, string_to_format, *args, **kwargs):
        self._cached_result = None
        self._string_to_format = string_to_format
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        if self._cached_result is None:
            self._cached_result = self._string_to_format\
                    .format(*self._args, **self._kwargs)
            self._string_to_format = None
            self._args = None
            self._kwargs = None
        return self._cached_result

    def __mod__(self, value):
        return str(self) % value


def remap_to_dict(data, include_index=False):
    """
    From a dictionnary of values, remap the different
    items to create a list of dictionnaries

    Example
    -------
        
    >>> items = remap_to_dict({'a': [1, 2], 'b': 1})
    ... [{'a': 1}, {'a': 2}, {'b': 1}]
    """
    items = []
    base_keys = list(data.keys())
    for key in base_keys:
        container = data[key]
        for i, item in enumerate(container):
            try:
                items[i][key] = item
            except:
                row = {key: item}
                # if include_index:
                #     row['id'] = i
                items.append(row)
    return items


def reverse_remap_to_dict(data):
    """
    From a list of dictionnaries of values, remap the 
    different items to create a dict where the keys
    are a list of values

    Parameters
    ----------

        data (list): [{'a': 1}, {'a': 2}]

    Returns
    -------

        list: list of dictionnaries

    >>> items = reverse_remap_to_dict([{'a': 1}, {'a': 2}, {'b': 1}])
    ... {'a': [1, 2], 'b': 1}
    """
    items = dict()
    for key in data[-0].keys():
        items.setdefault(key, [])

    for item in data:
        for key, value in item.items():
            items[key].append(value)
    return items
