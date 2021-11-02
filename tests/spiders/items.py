import os

from zineb.app import FileCrawler, Spider, Zineb
from zineb.settings import settings
from zineb.tests.models.items import ExampleModel, ExampleModel2
from zineb.utils.iteration import collect_files


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


# For collectfiles
os.environ.setdefault('ZINEB_SPIDER_PROJECT', 'zineb.tests.testproject.settings')
settings()

class FileCrawler1(FileCrawler):
    start_files = ['crawl.html']
    root_folder = 'media'


class FileCrawler2(FileCrawler):
    start_files = []


class FileCrawler3(FileCrawler):
    start_files = collect_files('media')
