import threading
import time

from zineb.utils.servers import DefaultServer
from zineb.logger import logger


class BaseReloader:
    @property
    def should_stop(self):
        return False    

    def run(self):
        raise NotImplemented
    

class StatReloader(BaseReloader):
    def run(self, main_thread, *args, **kwargs):
        logger.instance.info('Reloading')
        time.sleep(5)


def start_application(start_func, reloader=None, *args, **kwargs):
    main_thread = threading.Thread(target=start_func, args=args, kwargs=kwargs, name='zineb-main-thread')
    main_thread.daemon = True
    main_thread.start()
    
    if reloader is not None:
        while not reloader.should_stop:
            reloader.run(main_thread)
    

def run_with_reloader(start_func, *args, **kwargs):
    try:
        reloader = StatReloader()
        start_application(start_func, reloader=reloader, *args, **kwargs)
    except KeyboardInterrupt:
        logger.instance.info('Stopped')


def run_simple(start_func, *args, **kwargs):
    start_application(start_func, *args, **kwargs)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.instance.info('Stopped')

server = DefaultServer()
# run_simple(server.run)
run_with_reloader(server.run)





# @lru_cache(maxsize=1)
# def iter_modules_and_files():
#     pass


# class BaseReloader:
#     def run(self):
#         pass


# class StatReloader(BaseReloader):
#     pass


# def start_application(reloader, start_func, *args, **kwargs):
#     main_thread = threading.Thread(target=start_func, args=args, kwargs=kwargs, name='zineb-main-thread')
#     main_thread.daemon = True
#     main_thread.start()

#     while not reloader.should_stop:
#         reloader.run(main_thread)


# def run_with_reloader(start_func, *args, **kwargs):
#     """Starts the server with a reloader that detects
#     file changes"""
#     try:
#         reloader = StatReloader()
#         start_application(reloader, start_func, *args, **kwargs)
#     except KeyboardInterrupt:
#         pass


# def run_simple(start_func, *args, **kwargs):
#     """Runs the server without a reloader"""
#     main_thread = threading.Thread(target=start_func, args=args, kwargs=kwargs, name='zineb-main-thread')
#     main_thread.daemon = True
#     main_thread.start()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         pass

# s = run_with_reloader(some_function)
