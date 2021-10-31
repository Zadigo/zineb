import datetime
import os
import threading
import time
from functools import lru_cache

from zineb import global_logger
from zineb.registry import registry
from zineb.settings import lazy_settings

DEFAULT_SERVER_SLEEPING_TIME = 10


@lru_cache(maxsize=1)
def iter_modules_and_files():
    pass


class BaseServer:
    def __init__(self, *args, **kwargs):
        self.environ = os.environ

    def run(self):
        raise NotImplementedError('Subclasses should implement a run function')


class Server(BaseServer):
    def run(self, **kwargs):
        """Entrypoint for starting the server"""
        global_logger.logger.info('Starting server')

        initial_time = datetime.datetime.now()
        update_time = initial_time + datetime.timedelta(**lazy_settings.SERVER_CRON)
        tracked_time = None
        while True:
            current_time = datetime.datetime.now()
            print(current_time, tracked_time)

            if tracked_time is None:
                tracked_time = update_time

            if current_time > tracked_time:
                global_logger.logger.debug(f'Running spiders')

                spiders_to_run = getattr(lazy_settings, 'SERVER_EXECUTE_SPIDERS_ON_RELOAD', [])
                if spiders_to_run:
                    for name in spiders_to_run:
                        spider_config = registry.get_spider(name)
                        spider_config.run()
                else:
                    registry.run_all_spiders()
            time.sleep(DEFAULT_SERVER_SLEEPING_TIME)


class BaseReloader:
    def run(self):
        pass


class StatReloader(BaseReloader):
    pass


def start_application(reloader, start_func, *args, **kwargs):
    main_thread = threading.Thread(target=start_func, args=args, kwargs=kwargs, name='tweeter-main-thread')
    # main_thread.setDaemon(True)
    main_thread.daemon = True
    main_thread.start()

    while not reloader.should_stop:
        reloader.run(main_thread)


def run_with_reloader(start_func, *args, **kwargs):
    """Starts the server with a reloader that detects
    file changes"""
    try:
        reloader = StatReloader()
        start_application(reloader, start_func, *args, **kwargs)
    except KeyboardInterrupt:
        pass


def run_simple(start_func, *args, **kwargs):
    """Runs the server without a reloader"""

    main_thread = threading.Thread(target=start_func, args=args, kwargs=kwargs, name='zineb-main-thread')
    # main_thread.setDaemon(True)
    main_thread.daemon = True
    main_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
