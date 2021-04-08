import time
from typing import Any, Callable, Mapping

from pydispatch import dispatcher

from zineb.signals import signal
from zineb.logger import create_logger

logger = create_logger('Wait')

class Wait:
    def __init__(self, wait_time: int=5, 
                 callback: Callable[[Mapping], Any] = None, **parameters):
        self.result = None
        
        signal.send(dispatcher.Any, self, tag='Pre.Wait')
        logger.info(f"Waiting for {wait_time} seconds...")
        time.sleep(wait_time)

        if callback is not None:
            if callable(callback):
                self.result = callback(**parameters)
            else:
                raise TypeError(f"Callback should be a callable. Got {callback}")
        signal.send(dispatcher.Any, self, tag='Post.Wait')
