import datetime
import os
import time

from zineb import global_logger
from zineb.registry import registry
from zineb.settings import lazy_settings
from zineb.utils import time_formats
from zineb.utils.module_loader import import_from_module

DEFAULT_SERVER_SLEEPING_TIME = 10


class BaseServer:
    """Server used to persist the spiders
    
    N.B. This is a not an HTTP server which
    can deal with web requests"""

    def __init__(self, *args, **kwargs):
        self.environ = os.environ
        self.server_options = getattr(lazy_settings, 'SERVER')['options']

    def run(self):
        raise NotImplementedError('Subclasses should implement a run function')


class DefaultServer(BaseServer):
    def run(self, **options):
        """Entrypoint for starting the server"""
        initial_time = time_formats.now()
        update_time = initial_time + \
            datetime.timedelta(**self.server_options['cron'])
        tracked_time = None

        while True:
            current_time = time_formats.now()
            print(current_time, tracked_time)

            if tracked_time is None:
                tracked_time = update_time

            if current_time > tracked_time:
                global_logger.logger.debug(f'Running spiders')
                spiders_to_run = self.server_options['execute_spiders_on_reload']
                if spiders_to_run:
                    for name in spiders_to_run:
                        spider_config = registry.get_spider(name)
                        spider_config.run()
                else:
                    registry.run_all_spiders()

            time.sleep(DEFAULT_SERVER_SLEEPING_TIME)


def get_default_server():
    """Return the default server fro this application"""
    server_options = lazy_settings.SERVER
    try:
        return import_from_module(server_options['default'])
    except:
        return DefaultServer()
