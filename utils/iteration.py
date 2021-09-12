import os
from functools import lru_cache
from typing import Callable, Iterable

from zineb import exceptions
from zineb.settings import settings


def keep_while(func: Callable, values: Iterable):
    """
    A custom keep_while function that does not stop
    on False but completes all the list

    Parameters
    ----------

        func (Callable): [description]
        values (Iterable): [description]

    Yields
    ------

        Any: value to return
    """
    for value in values:
        result = func(value)
        if result:
            yield value


def drop_while(func: Callable, values: Iterable):
    """
    A custom drop_while function that does not stop
    on True but completes all the list

    Parameters
    ----------

        func (Callable): [description]
        values (Iterable): [description]

    Yields
    ------
    
        Any: value to return
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

    Parameters
    ----------

        func (Callable): [description]
        values (Iterable): [description]

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
    Collect all the files within specific
    directory of your project. This utility function
    is very useful with the FileCrawler:

        class Spider(FileCrawler):
            start_files = collect_files('some/path')

    Parameters
    ----------

        - path (str): relative path to the directory
        - func (Callable): a callback function to use on the files 

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
        return map(func, files)

    return files