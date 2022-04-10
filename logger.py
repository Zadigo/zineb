import logging

from zineb.settings import settings

# TODO: When testing Zineb from a global perspective
# via the test_project, the global settings is not
# yet set making that the log happens both at the
# project's root and at the zineb project

class Logger:
    def __init__(self, name: str=None, **kwargs):
        if name is None:
            name = self.__class__.__name__

        logger = logging.getLogger(name)
        # handler = logging.StreamHandler()

        # logger.addHandler(handler)
        # logger.setLevel(getattr(settings, 'LOG_LEVEL', logging.DEBUG))
       
        log_format = getattr(settings, 'LOG_FORMAT', '%(asctime)s - [%(name)s] %(message)s')
        formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%S')
       
        # handler.setFormatter(formatter)
        
        # if settings.LOG_TO_FILE:
        # TODO: Let the user choose if he wants
        # to log to a given file
        file_handler = logging.FileHandler(settings.LOG_FILE_NAME)
        logger.addHandler(file_handler)
        file_handler.setFormatter(formatter)
            
        self.instance = logger

    # def __call__(self, name=None, **kwargs):
    #     self.__init__(name=name, **kwargs)
    #     return self.logger

    @classmethod
    def create(cls, name: str=None):
        instance = cls(name=name)
        return instance


logger = Logger('Zineb')
