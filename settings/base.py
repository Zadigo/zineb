import os

PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

SETTINGS_FILE = os.path.join(PROJECT_PATH, 'settings', 'base.py')

# You can set up a basic database that can be
# used to store the data that you retrieve

# DATABASE = {
#     'name': None,
#     'backend': 'sqlite'
# }

# Use this configuration file to monitor, configure... the
# way your spider will be crawling the internet

CONFIGURATION_FILE = os.path.join(PROJECT_PATH, 'settings', 'project.conf')


LOG_TO_FILE = False

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'

LOG_FILE = None

LOG_LEVEL = 'DEBUG'



# A set of codes that will be executed before or after
# certain specific actions within the application

MIDDLEWARES = [
    'zineb.middlewares.user_agent.UserAgent'
]
