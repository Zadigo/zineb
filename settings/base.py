import os
import logging



PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

SETTINGS_FILE = os.path.join(PROJECT_PATH, 'settings', 'base.py')


# You an limit the scrapping to certain amount of
# domains. Register the acceptable domains to scrap
# in the list below

DOMAINS = []

# Ensure that every request is sent if and only if
# the scheme is HTTPS

ENSURE_HTTPS = False


# Use this configuration file to monitor and configure the
# way your spider will be crawling the internet

CONFIGURATION_FILE = os.path.join(PROJECT_PATH, 'settings', 'project.conf')


# Logging is done primaryly in the console.
# It is however possible to log to a file by
# specifying the LOG_TO_FILE parameter

LOG_TO_FILE = False

LOG_FILE = os.path.join(PROJECT_PATH, 'zineb.logs')

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

LOG_LEVEL = logging.DEBUG


# A set of codes that will be executed before or after
# certain specific actions within the application

MIDDLEWARES = [
    'zineb.middlewares.core.ApplicationChecks',
    'zineb.middlewares.user_agent.UserAgent',
    'zineb.middlewares.history.History'
]


# Use this to set a base set of headers for
# every HTTP request in the application

HEADERS = {}


# Register all the steps that were run by
# the application. This includes HTTP requests,
# download history or file creation history

HISTORY = False
