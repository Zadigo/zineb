import logging

from zineb.settings import settings

class Logger:
    def __init__(self, name=None, **kwargs):
        if name is None:
            name = self.__class__.__name__
            
        log_settings = settings.LOGGING

        logger = logging.getLogger(name)
        handler = logging.StreamHandler()

        logger.addHandler(handler)
        logger.setLevel(log_settings['level'] or logging.DEBUG)
       
        log_format = log_settings['format'] or '%(asctime)s - [%(name)s] %(message)s'
        formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%S')
       
        handler.setFormatter(formatter)
        
        file_handler = logging.FileHandler(log_settings['file_path'] or settings.GLOBAL_ZINEB_PATH)
        logger.addHandler(file_handler)
        file_handler.setFormatter(formatter)
            
        self.instance = logger

    @classmethod
    def create(cls, name: str=None):
        instance = cls(name=name)
        return instance


logger = Logger('Zineb')
