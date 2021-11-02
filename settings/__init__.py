import importlib
import os

# from pydispatch import dispatcher
from zineb.settings import base as initial_project_settings
from zineb.utils.functionnal import LazyObject


class UserSettings:
    SETTINGS_MODULE = None

    def __init__(self, dotted_path: str):
        self.configured  = False
        if dotted_path is None:
            # If this class is called outside of a project,
            # the dotted path will be None. Just ignore
            # and consider that there is not project
            # settings.py file to be used
            pass
        else:
            module = importlib.import_module(dotted_path)
            for key in dir(module):
                if key.isupper():
                    setattr(self, key, getattr(module, key))
            self.configured = True

            self.SETTINGS_MODULE = module

    def __repr__(self):
        return f"<{self.__class__.__name__}(configured={self.is_configured})>"

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    @property
    def is_configured(self):
        return self.configured


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

        list_or_tuple_settings = ['RETRY_HTTP_CODES', 'MIDDLEWARES', 'DEFAULT_REQUEST_HEADERS']
        # This is the section that implements the settings that
        # the user modified or implemented to the global settings
        project_settings_dotted_path = os.environ.get('ZINEB_SPIDER_PROJECT')
        self._user_settings = UserSettings(project_settings_dotted_path)
        for key in self._user_settings.__dict__.keys():
            if key.isupper():
                if key not in list_or_tuple_settings:
                    setattr(self, key, getattr(self._user_settings, key))
                else:
                    # In order to ensure that both the user setting
                    # and the global setting are used simultanuously, 
                    # when when dealing with tuples, lists [...] we have 
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

        # If the LOG_FILE setting stays at None,
        # it breaks the whole program since the
        # logger cannot work properly if to_file
        # is set to true
        LOG_FILE_NAME = getattr(self, 'LOG_FILE_NAME')
        if LOG_FILE_NAME is None:
            project_path = (
                getattr(self, 'PROJECT_PATH') or 
                getattr(self, 'GLOBAL_ZINEB_PATH')
            )
            log_file_path = os.path.join(project_path, LOG_FILE_NAME)
            setattr(self, 'LOG_FILE_NAME', log_file_path)

    def __call__(self, **kwargs):
        self.__init__()
        self.__dict__.update(kwargs)
        # Alert all middlewares and registered
        # signals on Any that the settings
        # have changed
        # TODO:
        # signal.send(dispatcher.Any, self)
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

settings = Settings()


class LazySettings(LazyObject):
    """
    This class implements a lazy loading of the settings
    for the application. In other words, the Settings class
    is cached and used only when called via the proxy class.
    """
    def _init_object(self):
        self.cached_object = Settings()

lazy_settings = LazySettings() 
