import importlib
import os
from typing import OrderedDict

from zineb.settings import base as initial_project_settings
from zineb.utils.functionnal import LazyObject
from zineb.utils.iteration import keep_while


class UserSettings:
    SETTINGS_MODULE = None

    def __init__(self, dotted_path):
        self.configured  = False
        if dotted_path is None:
            # If this class is called outside of a project,
            # the dotted path will be None. Just ignore
            # and consider that there is not project
            # settings.py file to be used
            pass
        else:
            module = importlib.import_module(f'{dotted_path}.settings')
            for key in dir(module):
                if key.isupper():
                    setattr(self, key, getattr(module, key))
            self.configured = True

            self.SETTINGS_MODULE = module

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value


class Settings:
    """ 
    Represents the settings file of the project. On project start,
    the project.settings file is parsed and stored in UserSettings.

    The base settings and user settings are merged and stored
    withing this class.
    """
    def __init__(self):
        for key in dir(initial_project_settings):
            if key.isupper():
                setattr(self, key, getattr(initial_project_settings, key, None))

        list_or_tuple_settings = ['RETRY_HTTP_CODES', 'MIDDLEWARES',
                                  'DEFAULT_REQUEST_HEADERS', 'DEFAULT_DATE_FORMATS', 
                                  'DOMAINS', 'USER_AGENTS', 'LOGGING', 'USER_AGENTS', 'STORAGES']
        # This is the section that implements the settings that
        # the user modified or implemented to the global settings
        # TODO: Use a global environment variable to get this ZINEB_SPIDER_PROJECT
        dotted_path = os.environ.get('ZINEB_SPIDER_PROJECT')
        self._user_settings = UserSettings(dotted_path)
        
        for key in self._user_settings.__dict__.keys():
            if key.isupper():
                if key not in list_or_tuple_settings:
                    setattr(self, key, getattr(self._user_settings, key))
                else:
                    # In order to ensure that both the user setting
                    # and the global setting are used simultanuously, 
                    # when dealing with tuples, lists [...] we have 
                    # to collide/extend these elements
                    user_setting = getattr(self._user_settings, key)
                    global_setting = getattr(self, key)
                    
                    if isinstance(user_setting, tuple):
                        user_setting = list(user_setting)

                    if isinstance(user_setting, list):
                        user_setting.extend(global_setting)
                    elif isinstance(user_setting, dict):
                        user_setting = user_setting | global_setting
                    setattr(self, key, user_setting)

        # If we do not have a path for the log file,
        # still set it by using either the project
        # path or the Zineb project - this allows
        # us to log to a file even though we didn't
        # have an initial path
        logging_settings = getattr(self, 'LOGGING')
        if logging_settings['file_path'] is None:
            self.LOGGING.update({'file_path': os.path.join(self.PROJECT_PATH or self.GLOBAL_ZINEB_PATH, logging_settings['name'])})

        # TODO: Send a signal when the Settings
        # class has been modified

    def __call__(self, **kwargs):
        self.__init__()
        self.__dict__.update(kwargs)
        # Alert all middlewares and registered
        # signals on Any that the settings
        # have changed
        
        # TODO: Send a signal when the settings
        # dict has changed

        return self.__dict__

    def __repr__(self):
        if self._user_settings.configured:
            return f"<{self.__class__.__name__} [{self._user_settings.__repr__()}]>"
        return f"<{self.__class__.__name__}>"

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def copy(self):
        return self.__dict__.copy()

    def get(self, key, default=None):
        return self.__dict__.get(key, default)
    
    def keys(self):
        return self.__dict__.keys()

    def has_setting(self, key):
        return key in self.__dict__.keys()
    
    def filter_by_prefix(self, prefix: str):
        sub_settings = OrderedDict()
        candidates = keep_while(lambda x: x.startswith(prefix), self.keys())
        for candidate in candidates:
            sub_settings[candidate] = self.__dict__[candidate]
        return sub_settings
      
      
class LazySettings(LazyObject):
    """
    This class implements a lazy loading of the settings
    for the application. In other words, the Settings class
    is cached and used only when called via the proxy class.
    """
    def _init_object(self):
        self.cached_object = Settings()


# FIXME: When I tried to access the MEDIA_FOLDER
# attribute on the lazy_settings instance, it
# returned None while being correctly set on 
#  settings instance above. There seems to be
# an issue in how the items are set on the
# lazy_settings instance
settings = LazySettings() 
