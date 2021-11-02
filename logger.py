import logging

from zineb.settings import settings as global_settings


class Logger:
    def __init__(self, name: str=None, debug_level=logging.DEBUG, 
                 to_file: bool=True, **kwargs):
        if name is None:
            name = self.__class__.__name__

        logger = logging.getLogger(name)
        handler = logging.StreamHandler()

        logger.addHandler(handler)
        logger.setLevel(debug_level)
        log_format = kwargs.get('log_format', '%(asctime)s - [%(name)s] %(message)s')
        formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%S')
        handler.setFormatter(formatter)

        if to_file:
            handler = logging.FileHandler(global_settings.LOG_FILE)
            logger.addHandler(handler)

        handler.setFormatter(formatter)
        self.logger = logger

    def __getattr__(self, name):
        return getattr(self.logger, name)

    def __call__(self, name=None, **kwargs):
        self.__init__(name=name, **kwargs)
        return self.logger

    @classmethod
    def new(cls, name=None, to_file=False, **kwargs):
        instance = cls(name=name, to_file=to_file, **kwargs)
        return instance
