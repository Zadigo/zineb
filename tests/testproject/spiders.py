from zineb.app import Zineb
from zineb.tests.testproject.models.base import SimpleModel

# Create your spiders here

class MySpider(Zineb):
    start_urls = [
        'http://example.com'
    ]

    def start(self, response, request, **kwargs):
        model = SimpleModel()
        model.add_value('url', response.find('a')['href'])
        print(model)
        