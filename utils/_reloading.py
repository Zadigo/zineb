import threading
import logging
import time

logger = logging.getLogger('Reloader')



class ReloaderError(Exception):
    pass


class BaseReloader:
    SLEEPING_TIME = 1

    def __init__(self):
        self._stop_condition = threading.Event()

    @property
    def should_stop(self):
        # The flag is set to False all time
        # there is not indication that that
        # the thread should stop
        return self._stop_condition.is_set()

    def stop(self):
        return self._stop_condition.set()

    def loop(self):
        events = self.events()

    def events(self):
        while True:
            time.sleep(self.SLEEPING_TIME)
            yield

    def run(self, main_thread):
        logging.debug('Autoreload started')
        self.loop()



class StatReloader(BaseReloader):
    pass


def start_server(reloader, func, *args, **kwargs):
    main_thread = threading.Thread(target=func, args=args, kwargs=kwargs, name='zineb-thread')
    main_thread.setDaemon(True)
    main_thread.start()

    while not reloader.should_stop:
        try:
            reloader.run(main_thread)
        except ReloaderError:
            logger.debug('Some error')

def some_function():
    pass


start_server(StatReloader(), some_function)
