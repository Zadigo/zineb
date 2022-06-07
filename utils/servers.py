import datetime
import os
import time

from zineb.logger import logger
from zineb.registry import registry
from zineb.settings import settings
from zineb.utils import time_formats
from zineb.utils.module_loader import import_from_module

DEFAULT_SERVER_SLEEPING_TIME = 10


class BaseServer:
    """Server used to persist the spiders
    
    N.B. This is a not an HTTP server and therefor
    cannot deal with web requests"""

    def __init__(self, *args, **kwargs):
        self.environ = os.environ
        self._server_options = getattr(settings, 'SERVER')['options']
        self.cron = self._server_options['cron']
        self.spiders_to_run = self._server_options['execute_spiders_on_reload']

    def run(self):
        raise NotImplementedError('Subclasses should implement a run function')


class DefaultServer(BaseServer):
    def run(self, **options):
        """Entrypoint for starting the server"""
        # initial_time = time_formats.now()
        # FIXME: We have to find a way to get a future
        # time from the current time inside the loop and
        # making sure that there is a possibility for
        # the current time to cross the future time
        # update_time = initial_time + datetime.timedelta(**self.cron)
        def update_time(d=None):
            if d is None:
                d = time_formats.now()
            return d + datetime.timedelta(**self.cron)
        
        tracked_time = None

        while True:
            current_time = time_formats.now()
            
            if tracked_time is None:
                tracked_time = update_time(d=current_time)

            if current_time > tracked_time:
                logger.instance.info(f'Running spiders')
                
                if registry.has_spiders:
                    if self.spiders_to_run:
                        for name in self.spiders_to_run:
                            spider_config = registry.get_spider(name)
                            spider_config.run()
                    else:
                        registry.run_all_spiders()
                tracked_time = None
            # logger.instance.debug(f'current: {current_time}, tracked: {tracked_time}')
            time.sleep(DEFAULT_SERVER_SLEEPING_TIME)


def get_default_server():
    """Return the default server fro this application"""
    server_options = settings.SERVER
    try:
        return import_from_module(server_options['default'])
    except:
        return DefaultServer()
