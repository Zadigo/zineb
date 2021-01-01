import datetime
import sched
import time
from threading import Timer

from zineb.utils.general import create_logger
from zineb.app import Zineb


class Monitor:
    def __init__(self, spider, kwargs:dict = {}):
        self.logger = create_logger(self.__class__.__name__)
        self.spider = spider
        if not issubclass(spider, Zineb):
            raise TypeError('Spider should be a subclass of Zineb')
        self.instance = self.spider(**kwargs)

    def start(self, interval=1, max=0):
        self.logger.info('Monitor is running...')
        time.sleep(10)
        # start_time = datetime.datetime.now()

        # previous_start_time = None
        # next_start_time = None
        # max_occurences = 0

        # delta = datetime.timedelta(minutes=interval)
        # next_start_time = start_time + delta
        # previous_start_time = next_start_time

        # while True:
        #     current_time = datetime.datetime.now()
        #     if current_time >= next_start_time:
        #         self.instance()
        #         self.logger.info(f'Executed < {self.spider} >')
        #         time.sleep(1)

        #         next_start_time = previous_start_time + delta
        #         previous_start_time = next_start_time

        #         if max > 0:
        #             max_occurences = max + 1

        #             if max_occurences == max:
        #                 break
