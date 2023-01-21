import os
from functools import lru_cache
from importlib import import_module

from zineb.utils.formatting import LazyFormat


def import_from_module(dotted_path: str):
    """
    Imports a module, gets an object then
    tries to return it
    """
    try:
        path, klass = dotted_path.rsplit('.', maxsplit=1)
    except:
        raise ImportError(
            LazyFormat("Module at path {path} does not exist.", path=dotted_path)
        )

    module = import_module(path)

    try:
        return getattr(module, klass)
    except AttributeError:
        raise ImportError(LazyFormat("Could not find attribute '{klass}' "
        "in module {dotted_path}.", klass=klass, dotted_path=dotted_path))


def module_directory(module):
    """Return the main directory of a module"""
    paths = list(getattr(module, '__path__', []))
    if len(paths) == 1:
        return paths[0]
    else:
        filename = getattr(module, '__file__', None)
        if filename is not None:
            return os.path.dirname(filename)
    raise ValueError("Could not determine module's directory.")
