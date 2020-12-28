import os
import logging



PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

SETTINGS_FILE = os.path.join(PROJECT_PATH, 'settings', 'base.py')


# Register all your spiders from your
# project here

SPIDERS = []


# You an limit the scrapping to certain amount of
# domains. Register the acceptable domains to scrap
# in the list below

DOMAINS = []

# Ensure that every request is sent if and only if
# the scheme is HTTPS

ENSURE_HTTPS = False


# Use this configuration file to monitor and configure the
# way your spider will be crawling the internet

CONFIGURATION_FILE = os.path.join(PROJECT_PATH, 'settings', 'zineb.conf')


# Logging is done primaryly in the console.
# It is however possible to log to a file by
# specifying the LOG_TO_FILE parameter

LOG_TO_FILE = True

LOG_FILE = os.path.join(PROJECT_PATH, 'zineb.logs')

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

LOG_LEVEL = logging.DEBUG


# A set of codes that will be executed before or after
# certain specific actions within the application

MIDDLEWARES = [
    'zineb.middlewares.handlers.Handler',
    # 'zineb.middlewares.referer.Referer',
    'zineb.middlewares.history.History',
    'zineb.middlewares.statistics.GeneralStatistics'
]


# A list of custom user agents that can be used by the
# spider in addition to the ones that were already implemented

USER_AGENTS = []

RANDOMIZE_USER_AGENTS = False


# Use this to set a base set of headers for
# every HTTP request in the application

HEADERS = {}


# Register all the steps that were run by
# the application. This includes HTTP requests,
# download history or file creation history

HISTORY = False


# Set a list of proxies to use within the project.
# The proxies will be used randomly so make sure they
# are fully/regularly functionnal.

PROXIES = []


# How to handle HTTP retries when a request
# fails based on a given HTTP code

RETRY = False

RETRY_TIMES = 2

RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
