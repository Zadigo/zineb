import importlib
from collections import OrderedDict


class Settings:
    """ 
    Represents the settings file of the project

    Returns
    -------

        OrderedDict: [description]
    """
    _settings = OrderedDict()

    def __init__(self):
        from zineb.utils.general import create_logger

        settings = importlib.import_module('zineb.settings.base')
        modules_dict = settings.__dict__

        for key, value in modules_dict.items():
            if key.isupper():
                self._settings.setdefault(key, value)
                # Also allow something like
                # settings.MY_SETTING when using
                # the Settings instance
                self.__dict__[key] = value

        logger = create_logger(self.__class__.__name__)
        logger.info(f"Loaded project settings...")

    def __call__(self, **kwargs):
        self.__init__()
        self._settings.update(kwargs)
        return self._settings
    
    def __str__(self) -> str:
        return str(self._settings)

    def __getitem__(self, key):
        return self._settings[key]

    def __iter__(self):
        return iter(self._settings)

    def copy(self):
        return self._settings.copy()

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def has_setting(self, key):
        return key in self._settings.keys()

settings = Settings()
