import os
from importlib import import_module
from typing import Tuple

from zineb.db.migrations.base import Migrations
from zineb.settings import lazy_settings
from zineb.db.migrations.store import MigrationStore

class MigrationFilesLoader:
    """
    This class will load every migration file
    present in the given project via the migrations
    directory. Each file should have a unique
    Migration class that subclasses Migrations.
    
    This class can work as a two way process where
    it works both the the database and with the local
    migrations directory.
    """

    def __init__(self, connection=None):
        self.migrations = MigrationStore()
        
    @staticmethod
    def check_naming_convention(name) -> Tuple[int, str]:
        items = name.split('.')[-1]
        number, rhv = name.rsplit('_', maxsplit=1)
        if not isinstance(number, int):
            pass
        return number, rhv

    def load_files(self):
        store = MigrationStore()
        
        _, _, files = next(os.walk('./db/test_migrations'))
        for file in files:
            name, extension = file.split('.')
            if extension == 'py':
                module = import_module(f"db.test_migrations.{name}")
                module_name = getattr(module, '__name__')
                
                if not module_name.endswith('__init__'):
                    klass = getattr(module, 'Migration')

                    # 1. Check that the files that we
                    # are collecting respect a specific
                    # name convention
                    number, rhv = self.check_naming_convention(module_name)

                    if not issubclass(klass, Migrations):
                        raise ValueError('This is not a subclass of Migrations')

                    self.migrations.add(module_name, module, numbering=number, rhv=rhv)


l = MigrationFilesLoader()
l.load_files()
print(l.migrations)
