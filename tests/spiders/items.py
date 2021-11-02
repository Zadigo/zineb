from zineb.app import Zineb, Spider
from zineb.tests.models.items import ExampleModel, ExampleModel2

class SpiderSubclass(Spider):
    start_urls = ['http://example.com']
    

class SimpleSpider(Zineb):
    start_urls = ['http://example.com']



class MetaSpider(Zineb):
    class Meta:
        domains = ['example.com']


class SpiderWithMultiple(Zineb):
    start_urls = [
        'http://example.com'
    ]

    _temp_model_holder = []

    def start(self, response, **kwargs):
        model = ExampleModel()
        model.add_value('url', response.find('a')['href'])
        model2 = ExampleModel2()
        model2.add_value('value', response.find('a').text)
        self._temp_model_holder.extend([model, model2])



class SpiderWithMultipleDomains(Zineb):
    start_urls = [
        'http://example.com',
        'http://example.com'
    ]

    def start(self, response, **kwargs):
        model = ExampleModel()
        model.add_value('url', response.find('a')['href'])
