import os
import re
from functools import lru_cache
from typing import Callable, Iterable, Union

from importlib_metadata import itertools

from zineb import exceptions
from zineb.settings import settings


def keep_while(func: Callable, values: Iterable):
    """
    A custom keep_while function that does not stop
    iterating on the first False result 
    but completes all the list
    """
    for value in values:
        result = func(value)
        if result:
            yield value


def drop_while(func: Callable, values: Iterable):
    """
    A custom keep_while function that does not stop
    iterating on the first False result 
    but completes all the list
    """
    for value in values:
        result = func(value)
        if not result:
            yield value


def split_while(func: Callable, values: Iterable):
    """
    Splits a set of values in seperate lists
    depending on whether the result of the function
    return True or False

    Returns
    -------

        tuple: ([true values], [false values])
    """
    a = [value for value in values if func(value)]
    b = [value for value in values if not func(value)]
    return a, b


@lru_cache(maxsize=0)
def collect_files(path: str, func: Callable = None):
    """
    Collect all the files within a specific
    directory of your project. This utility function
    is very useful with the FileCrawler.

        class Spider(FileCrawler):
            start_files = collect_files('some/path')

    Parameters
    ----------

        - path (str): relative path to the directory
        - func (Callable): a func that can be used to filter the files

    Raises
    ------

        - ValueError: [description]

    Returns
    -------

        - Iterator: list of files
    """
    if settings.PROJECT_PATH is None:
        raise exceptions.ProjectNotConfiguredError()

    full_path = os.path.join(settings.PROJECT_PATH, path)
    if not os.path.isdir(full_path):
        raise ValueError('Path should be a directory')

    root, _, files = list(os.walk(full_path))[0]
    if full_path:
        files = map(lambda x: os.path.join(root, x), files)

    if func is not None:
        return filter(func, files)

    return files


def regex_iterator(text: str, regexes: Union[tuple, list]):
    """
    Check a text string against a set of regex values

    Parameters
    ----------

        - text (str): a string to test
        - regexes (Union[tuple, list]): a tuple/list of regexes
    """
    result = None
    for regex in regexes:
        result = re.search(regex, text)
        if result:
            result = result.groups()
    return result


# def create_batch(values: list, by: int=10):
#     batches = []
#     batch = []
#     for i, value in enumerate(values):
#         if i + 1 % by == 0:
#             batches.append(batch)
#             batch = []
#         else:
#             batch.append(value)
        
#     return batches


# print(create_batch(list(range(0, 20))))

def iterate_by_chunk(items, chunk_size=100):
    """Create chunks in order to improve
    iteration performance e.g. [(..., ...), ...]"""
    iterator = iter(items)
    while True:
        chunk = tuple(itertools.islice(iterator, chunk_size))
        if not chunk:
            break
        yield chunk
