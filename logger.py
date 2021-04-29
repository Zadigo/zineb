import logging
from zineb.settings import settings as global_settings


class Logger:
    def __init__(self, name=None, debug_level=logging.DEBUG, 
                 to_file=True, **kwargs):
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

    def __call__(self, name=None, debug_level=logging.DEBUG, 
                 to_file=False, **kwargs):
        self.__init__(name=name, debug_level=debug_level, 
                      to_file=to_file, **kwargs)
        return self.logger
