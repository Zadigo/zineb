import logging
import os
from zineb.settings import settings
from zineb.exceptions import ProjectNotConfiguredError


class Logger:
    def __init__(self, name: str=None, **kwargs):
        if name is None:
            name = self.__class__.__name__

        logger = logging.getLogger(name)
        handler = logging.StreamHandler()

        logger.addHandler(handler)
        logger.setLevel(getattr(settings, 'LOG_LEVEL', logging.DEBUG))
        log_format = getattr(settings, 'LOG_FORMAT', '%(asctime)s - [%(name)s] %(message)s')
        formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%S')
        handler.setFormatter(formatter)

        if getattr(settings, 'LOG_TO_FILE', False):
            if settings.PROJECT_PATH is None:
                raise ProjectNotConfiguredError('In order to log to a file,'
                'a project needs to be configured.')
            
            # The full path of the log file is set when the
            # settings parameter is first called
            handler = logging.FileHandler(settings.LOG_FILE_NAME)
            logger.addHandler(handler)

        handler.setFormatter(formatter)
        self.logger = logger

    def __call__(self, name=None, **kwargs):
        self.__init__(name=name, **kwargs)
        return self.logger

    @classmethod
    def new(cls, name=None, to_file=False, **kwargs):
        instance = cls(name=name, to_file=to_file, **kwargs)
        return instance


global_logger = Logger('Zineb')
