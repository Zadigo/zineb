from zineb.app import Spider
from zineb.settings import settings
from tests.testproject.models import SimpleModel

# Create your spiders here


class MySpider(Spider):
    start_urls = ['http://example.com']

    def start(self, response, **kwargs):
        model = SimpleModel()
        model.add_value('url', response.find('a')['href'])
