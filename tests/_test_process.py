# import datetime

# import pytz
# from zineb.models.fields import AgeField, DateField

# t = pytz.timezone('America/Chicago')
# c = datetime.datetime.now().astimezone(t)
# d = datetime.datetime.strptime('2018-01-01', '%Y-%M-%d')
# c = d.astimezone(t)

# d = datetime.datetime.strptime('1-1-2017', '%d-%M-%Y')
# print(d.date())


# from functools import cached_property, partial

# from bs4 import BeautifulSoup
# from zineb.extractors.base import ImageExtractor
# from zineb.models.fields import ImageField
# from zineb.utils.processors import UrlProcessor
# from zineb.utils.urls import replace_urls_suffix

# e = ImageExtractor(url_must_contain='130x170', replace_suffix=True, processors=[UrlProcessor(replace_urls_suffix)])

# with open('tests/html/images.html') as f:
#     s = BeautifulSoup(f, 'html.parser')
#     e.resolve()

# print(e[0].attrs)


import subprocess
from zineb import setup
import os

os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'tests.testproject')
setup()

from zineb.registry import registry
registry.get_default_storage()
