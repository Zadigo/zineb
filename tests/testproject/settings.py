import os


PROJECT_PATH = os.path.dirname(__file__)


# Register all your spiders from your
# project here and then call
# python manage.py start to execute all
# of them or python manage.py <spider name>

SPIDERS = ['MySpider']


# A set of codes that will be executed before or after
# certain specific actions within the application

MIDDLEWARES = []

LOAD_MODELS = True
