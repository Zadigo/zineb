import inspect
import os
import warnings
from collections import OrderedDict, defaultdict
from functools import lru_cache
from importlib import import_module
from pathlib import Path

import pytz

from zineb.exceptions import RequiresProjectError, SpiderExistsError
from zineb.logger import logger
from zineb.middleware import Middleware

SPIDERS_MODULE = 'spiders'

MODELS_MODULE = 'models'

ENVIRONMENT_VARIABLE = 'ZINEB_SPIDER_PROJECT'


class ModelsDescriptor:
    models = {}
    
    def __get__(self, instance, cls=None):
        return self.models[instance]


class SpiderConfig:
    """
    Class that represents a spider and 
    its overall difference
    """

    def __init__(self, name, spiders_module):
        self.name = name
        self.dotted_path = None
        self.registry = None
        self.spider_class = getattr(spiders_module, name, None)
        
        self.MODULE = spiders_module

        paths = list(getattr(self.MODULE, '__path__', []))
        if not paths:
            filename = getattr(self.MODULE, '__file__', None)
            if filename is not None:
                paths = [os.path.dirname(filename)]

        # if len(paths) > 1:
        #     raise ValueError("There are multiple modules "
        #     "trying to start spiders")

        if not paths:
            raise ValueError("No spiders module within your project. "
            "Please create a 'spiders.py' module.")

        self.path = paths[0]
        self.is_ready = False

    def __repr__(self):
        return f"<{self.__class__.__name__} for {self.name}>"
    
    @classmethod
    def create(cls, name, module):
        instance = cls(name, module)
        return instance
    
    def check_ready(self):
        if self.spider_class is not None and self.name is not None:
            self.is_ready = True

    def run(self):
        """Runs the spider by calling the spider class
        which in return calls "start" method on the
        spider via the __init__ method"""
        if self.spider_class is None:
            raise ValueError(f'Could not start spider in project: {self.dotted_path}')
        self.spider_class()
        
    # def load_models(self):
    #     try:
    #         models_module = import_module(f'{self.dotted_path}.{MODELS_MODULE}')
    #     except:
    #         # If we could not get a module for the
    #         # models just continue
    #         models_module = None
    #     else:
    #         from zineb.models.datastructure import Model
            
    #         if models_module is not None:
    #             all_models = inspect.getmembers(models_module, inspect.isclass)
    #             models = filter(lambda x: isinstance(x[1], Model), all_models)
                
    #             for name, model in models:
    #                 self.all_models[name] = model
                    
    #             for spider in self.spiders.values():
    #                 descriptor = ModelsDescriptor()
    #                 descriptor.models = self.all_models
    #                 setattr(spider, 'models', descriptor)
    

class MasterRegistry:
    """
    Main registry for a zineb project
    """
    def __init__(self):
        self.is_ready = False
        self.spiders_ready = False
        self.models_ready = False
        self.spiders = OrderedDict()
        self.all_models = defaultdict(dict)
        self.project_name = None
        self.absolute_path = None
        self.middlewares = []
        self.storages = {'default': {}}

    def __repr__(self):
        return f"<{self.__class__.__name__}[{dict(self.spiders)}]>"

    @property
    def has_spiders(self):
        return len(self.spiders.keys()) > 0

    @lru_cache(maxsize=1)
    def get_spiders(self):
        return self.spiders.values()

    def has_spider(self, name):
        return name in self.spiders

    def check_spiders_ready(self):
        if not self.has_spiders:
            raise ValueError(("Spiders are not yet loaded or "
            "there are no registered ones."))

    def check_spider_exists(self, name):
        return name in self.spiders.keys()

    def get_spider(self, spider_name: str):
        self.check_spiders_ready()
        try:
            return self.spiders[spider_name]
        except KeyError:
            self.local_logger.logger.error((f"The spider with the name '{spider_name}' does not "
            f"exist in the registry. Available spiders are {', '.join(self.spiders.keys())}. "
            f"If you forgot to register {spider_name}, check your settings file."), stack_info=True)
            raise SpiderExistsError(spider_name)
        
    def get_default_storage(self):
        name, instance = list(self.storages['default'].items())[0]
        return instance
        
    def preconfigure_project(self, dotted_path, settings):
        # Replace the log file name with the full path
        # to the project's log file 
        # setattr(settings, 'LOG_FILE_NAME', Path.joinpath(self.absolute_path, settings.LOG_FILE_NAME))
        setattr(settings, 'LOG_FILE_NAME', settings.PROJECT_PATH.joinpath(settings.LOG_FILE_NAME))

        # If the user did not explicitly set the path
        # to a MEDIA_FOLDER, we will be doing it
        # autmatically here
        media_folder = getattr(settings, 'MEDIA_FOLDER')
        if media_folder is None:
            # setattr(settings, 'MEDIA_FOLDER', Path.joinpath(self.absolute_path, 'media'))
            setattr(settings, 'MEDIA_FOLDER', settings.PROJECT_PATH.joinpath('media'))
                
        try:
            # Change TIME_ZONE to a pytz usable 
            # instance for the project
            instance = pytz.timezone(settings.TIME_ZONE)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f'Timezone specified in TIME_ZONE '
                'does not exist. Got: {settings.TIME_ZONE}')
        else:
            settings.TIME_ZONE = instance
                    
        self.is_ready = True
        
        # TODO: Load all the middlewares once everything
        # is setup and ready to run
        middlewares = Middleware()
        self.middlewares = middlewares
        
        # TODO: Send a signal when the master registry
        # has completed all the initial setting up
        
        # Load the current storage and store it as
        # an instance on the spider
        storages = settings.STORAGES
        for name, storage in storages.items():
            try:
                module_path, klass_name = storage.rsplit('.', maxsplit=1)
                storage_module = import_module(module_path)
            except:
                # TODO: Raise an error if we cannot get a file system
                # storage ?
                pass
            else:
                klass = getattr(storage_module, klass_name, None)
                if klass is not None:
                    from zineb.storages import BaseStorage
                    if inspect.isclass(klass) and BaseStorage in klass.__mro__:
                        instance = klass()
                        instance.prepare()
                        self.storages.update({name: {klass_name: instance}})
                    
                        
    def populate(self):
        """
        Populates the registry with the spiders 
        that were registered in the `SPIDERS` variable 
        in the settings.py file
        """        
        dotted_path = os.environ.get(ENVIRONMENT_VARIABLE, None)
        
        if dotted_path is None:
            # The user is lauching the application outside
            # of a project (standalone), it's
            # his responsibility to provide a module where
            # the spiders are located. This is done in order
            # to not completly block the project from functionning
            raise RequiresProjectError()
                
        try:
            project_module = import_module(dotted_path)
        except ImportError:
            raise ImportError('Could not find the related module')
        
        from zineb.app import Spider
        from zineb.settings import settings
        
        self.absolute_path = Path(project_module.__path__[0])
        self.project_name = self.absolute_path.name
        setattr(settings, 'PROJECT_PATH', self.absolute_path)
        
        try:
            # Try to load the spiders submodule specifically
            # to ensure that this is a zineb project
            spiders_module = import_module(f'{dotted_path}.{SPIDERS_MODULE}')
        except:
            raise ImportError("Failed to load the project's spiders submodule")
        
        # Check that there are class elements that we can used
        # and that ar subclassed by Spider that we can use
        elements = inspect.getmembers(spiders_module, predicate=inspect.isclass)
        
        valid_spiders = list(filter(lambda x: issubclass(x[1], Spider), elements))
        valid_spider_names = list(map(lambda x: x[0], valid_spiders))
        
        for name in settings.SPIDERS:
            if name not in valid_spider_names:
                raise ValueError(f'You are trying to trying to use a class that '
                    'is not a subclass of Zineb. Got: {name}')
                
            instance = SpiderConfig.create(name, spiders_module)
            self.spiders[name] = instance
            instance.regitry = self
        
        for config in self.spiders.values():
            config.check_ready()

        self.spiders_ready = True

        # Cache the registry in the settings
        # file for performance reasons
        settings['REGISTRY'] = self
        
        # TODO: Send a signal when the spider
        # registry has been populated

        self.preconfigure_project(dotted_path, settings)

    def run_all_spiders(self):
        if not self.has_spiders:
            warnings.warn(("There are no registered spiders in your project. If you created spiders, "
            "register them within the SPIDERS variable of your "
            "settings.py file."), Warning, stacklevel=0)
        else:
            for config in self.get_spiders():
                try:
                    # TODO: Send a signal before the spider has
                    # starting parsing
                    config.run()
                except Exception:
                    logger.instance.critical((f"Could not start {config}. "
                    "Did you use the correct class name?"), stack_info=True)
                    raise
                else:
                    # TODO: Send a signal once the spider has
                    # terminated the parsing
                    # signal.send(dispatcher.Any, self)
                    pass


registry = MasterRegistry()
