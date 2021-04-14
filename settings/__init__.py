import importlib
import os
import warnings

from pydispatch import dispatcher
from zineb._functionnal import LazyObject
from zineb.settings import base as global_settings
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
        for key in dir(global_settings):
            if key.isupper():
                # Also allow something like
                # settings.MY_SETTING when using
                # the Settings instance
                setattr(self, key, getattr(global_settings, key, None))

        # Load the user settings and update the global
        # settings with what the user has defined
        settings_containing_data = ['RETRY_HTTP_CODES', 'MIDDLEWARES', 'DEFAULT_REQUEST_HEADERS']
        user_settings_module = os.environ.get(USER_SETTINGS_ENV_VARIABLE_NAME)
        self._user_settings = UserSettings(user_settings_module)
        for key in self._user_settings.__dict__.keys():
            if key.isupper():
            # if key.isupper() and key not in settings_containing_data:
                setattr(self, key, getattr(self._user_settings, key))
            # else:
            #     # In order to ensure that both the user setting
            #     # and the global setting are used, we have to collide
            #     # both of these elements together
            #     user_setting = getattr(self._user_settings, key)
            #     global_setting = getattr(global_settings, key)
            #     user_setting.extend(global_setting)
            #     setattr(self, key, user_setting)

    def __call__(self, **kwargs):
        self.__init__()
        self.__dict__.update(kwargs)
        # Alert all middlewares and registered
        # signals on Any that the settings
        # have changed
        signal.send(dispatcher.Any, self)
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
    is cached and used only when functionnalities are used
    via the proxy class.
    """
    def _init_object(self):
        self.cached_object = Settings()

lazy_settings = LazySettings() 
