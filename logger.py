import logging

def create_logger(name, debug_level=logging.DEBUG, to_file=False, **kwargs):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()

    logger.addHandler(handler)
    logger.setLevel(debug_level)
    log_format = kwargs.get('log_format', '%(message)s')
    formatter = logging.Formatter(log_format, datefmt='%d-%m-%Y %H:%S')

    if to_file:
        handler = logging.FileHandler('zineb.log')
        logger.addHandler(handler)
        handler.setFormatter(formatter)

    handler.setFormatter(formatter)
    return logger
