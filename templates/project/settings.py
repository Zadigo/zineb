""" 
Implement all the settings for your project here.
To check all available settings for your project
consult: 
"""

import os


PROJECT_PATH = os.path.dirname(__file__)


# Register all your spiders from your
# project here

SPIDERS = [
    'MySpider'
]


# A set of codes that will be executed before or after
# certain specific actions within the application

MIDDLEWARES = [
    'zineb.middlewares.handlers.Handler',
    'zineb.middlewares.history.History',
    'zineb.middlewares.statistics.GeneralStatistics'
]
