from typing import Type
from zineb.settings import settings
from importlib import import_module


class LoadDatabase:
    def __init__(self):
        database_settings = settings.DATABASE
        backend_python_path = database_settings.get('backend')
        path, name = backend_python_path.rsplit('.', 1)
        module = import_module(path)
        backend = getattr(module, name)
        self.backend = backend(database_settings.get('name'))
        
init_database = LoadDatabase()


def get_database_backend() -> Type:
    return init_database.backend
