import os
import logging

# Global path that stores the path to the Zineb
# main directory. This is useful for functionalities
# that require using this for various tasks

GLOBAL_ZINEB_PATH = os.path.dirname(os.path.dirname(__file__))

PROJECT_PATH = None


# Register all your spiders from your
# project here

SPIDERS = []


# Specifies whether the models should
# loaded on project startup

LOAD_MODELS = False


# Limit scrapping to certain specific amount of
# domains by invalidating those that do not respect
# the given list

DOMAINS = []

# Ensure that every request is sent if and only if
# the scheme is HTTPS

ENSURE_HTTPS = False


# Logging is done primaryly in the console.
# It is however possible to log to a file by
# specifying the LOG_TO_FILE parameter

LOGGING = {
    'name': 'zineb.log',
    'file_path': None,
    'format': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    'level': logging.DEBUG,
    'log_to_file': False
}


# A set of codes that will be executed before or after
# certain specific actions within the application

MIDDLEWARES = [
    # 'zineb.middlewares.referer.Referer',
    # 'zineb.middlewares.history.History',
    # 'zineb.middlewares.statistics.GeneralStatistics'
    # 'zineb.middlewares.wireframe.WireFrame',
]


# A list of custom user agents that can be used by the
# spider in addition to the ones that were already implemented

USER_AGENTS = []

RANDOMIZE_USER_AGENTS = False


# Use this to set a base set of headers for
# every HTTP request in the application

DEFAULT_REQUEST_HEADERS = {
    'Accept-Language': 'en',
    'Accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referrer': 'https://google.com',
}


# Register all the steps that were run by
# the application. This includes HTTP requests,
# download history or file creation history

# HISTORY = False


# Set a list of proxies to use
# structured as (http, 1.1.1.1) 
# or (http, http://1.1.1.1)

PROXIES = []


# How to handle HTTP retries when a request
# fails based on a given HTTP code

RETRY = False

RETRY_TIMES = 2

RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]


# The main folder to store all your downloaded
# files from the internet. This folder could
# also point to a folder in the cloud

# AWS_SECRET_KEY = None

# AWS_SOMETHING_KEY = None

# AWS_STORAGE_URL = 'https://example.com'

# The main folder of storing downloaded data
# or files that are being saved

MEDIA_FOLDER = None


# Specify a default storage class for managing content
# that was downloaded from the internet or files
# that were created with the model

STORAGES = {
    'default': 'zineb.storages.FileSystemStorage'
}


# Default date formats used for resolving
# DateField and AgeField values

DEFAULT_DATE_FORMATS = (
    '%Y-%m-%d',
    '%Y.%m.%d',
    '%Y/%m/%d',
    '%y-%m-%d',
    '%y.%m.%d',
    '%y/%m/%d',
    '%d-%m-%Y',
    '%d/%m/%Y',
    '%d.%m.%Y',
    '%d-%m-%y',
    '%d/%m/%y',
    '%d.%m.%y',
    '%Y %b %d',
    '%Y %b, %d',
    '%y %b %d',
    '%y %b, %d',
    '%d %b %Y',
    '%d %b, %Y',
    '%d %b %y',
    '%d %b, %y',
    '%b %d, %Y',
    '%b %d, %y'
)


# The default timezone to use for the
# application available choices can be
# found at https://en.wikipedia.org/wiki/List_of_tz_zones_by_name

TIME_ZONE = 'America/Chicago'
