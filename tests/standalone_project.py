from zineb.app import Zineb
from zineb.settings import settings
from zineb import initialize

settings(SPIDERS=['MySpider', 'MySpider2'])

class MySpider(Zineb):
    start_urls = ['http://example.com']


class MySpider2(Zineb):
    pass


# FIXME: Calls setup() a second time before
# even finishing the populate function. I think
# it's because calling setup in a module where
# setup tries to autoload it, makes that there
# is a double call
# initialize.setup('tests.standalone_project')
initialize.setup()

from zineb.registry import registry
print(registry)
