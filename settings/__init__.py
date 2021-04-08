import importlib
import os
import warnings

from pydispatch import dispatcher
from zineb._functionnal import LazyObject
from zineb.settings import base
from zineb.signals import signal

USER_SETTINGS_ENV_VARIABLE_NAME = 'ZINEB_SPIDER_PROJECT'

class UserSettings:
    SETTINGS_MODULE = None

    def __init__(self, user_settings_module: str):
        self.configured  = False
        if user_settings_module is None:
            warnings.warn('Using global settings as user did not define project settings', Warning)
        else:
            module = importlib.import_module(user_settings_module)
            for key in dir(module):
                if key.isupper():
                    setattr(self, key, getattr(module, key))
            self.configured = True

        self.SETTINGS_MODULE = user_settings_module

    def __repr__(self):
        return f"<{self.__class__.__name__}(configured={self.is_configured})>"

    @property
    def is_configured(self):
        return self.configured


class Settings:
    """ 
    Represents the settings file of the project

    Returns
    -------

        OrderedDict: [description]
    """
    def __init__(self):
        # settings = importlib.import_module('zineb.settings.base')
        # modules_dict = settings.__dict__
        # for key, value in modules_dict.items():

        for key in dir(base):
            if key.isupper():
                # self._settings.setdefault(key, value)
                # Also allow something like
                # settings.MY_SETTING when using
                # the Settings instance
                setattr(self, key, getattr(base, key, None))

        # Load the user settings and update the global
        # settings with what the user has defined
        user_settings_module = os.environ.get(USER_SETTINGS_ENV_VARIABLE_NAME)
        self._user_settings = UserSettings(user_settings_module)
        for key in self._user_settings.__dict__.keys():
            if key.isupper():
                setattr(self, key, getattr(self._user_settings, key))

    def __call__(self, **kwargs):
        self.__init__()
        self.__dict__.update(kwargs)
        # Alert all middlewares and registered
        # signals on Any that the settings
        # have changed
        signal.send(dispatcher.Any, self)
        return self.__dict__

    def __repr__(self):
        return f"<{self.__class__.__name__} ''>"

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def copy(self):
        return self.__dict__.copy()

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def has_setting(self, key):
        return key in self.__dict__.keys()

settings = Settings()


class LazySettings(LazyObject):
    """
    This class implements a lazy loading of the settings
    for the application. In other words, the Settings class
    is cached and used only when functionnalities are used
    via the proxy class.
    """
    def _init_object(self):
        self.cached_object = Settings()

lazy_settings = LazySettings() 
