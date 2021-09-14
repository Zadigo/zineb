from collections import defaultdict


class LazyFormat:
    """
    Lazily formats a string until it is called or required.

    Example
    -------

        message = LazyFormat('Kendall {name}', name='Jenner')

        >> str(message)
        >> Kendall Jenner
    """
    __slots__ = ('_cached_result', '_string_to_format', '_args', '_kwargs')

    def __init__(self, string_to_format: str, *args, **kwargs):
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


# def remap_to_dict(data: dict):
#     """
#     From a dictionnary of values, remap the different
#     items to create a list of dictionnaries

#     Example
#     -------
        
#         > {'a': [1, 2], 'b': 1} becomes
#           [{'a': 1}, {'a': 2}, {'b': 1}] 

#     Yields
#     ------

#         list:  list of dictionnaries
#     """
#     base = {}
#     for key in data.keys():
#         base.setdefault(key, None)

#     number_of_items = len(data[list(data.keys())[-0]])
#     container = []
#     for i in range(number_of_items):
#         container.append(base)

#     for key, values in data.items():
#         if isinstance(values, (list, tuple)):
#             for i, value in enumerate(values, start=0):
#                 container[i][key] = value
#     return container


def reverse_remap_to_dict(data: list):
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
    """
    items = dict()
    for key in data[-0].keys():
        items.setdefault(key, [])

    for item in data:
        for key, value in item.items():
            items[key].append(value)
    return items
