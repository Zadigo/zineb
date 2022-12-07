from zineb.app import Spider
from zineb.models.datastructure import Model
from zineb.models import fields
from zineb.models import functions

class SomeModel(Model):
    title = fields.CharField()
    content = fields.TextField()


class MySpider(Spider):
    start_urls = ['http://example.com']

    def start(self, response, request, **kwargs):
        title = response.find('h1')
        content = response.find('p')
        model = SomeModel()
        model.add_value('title', title)
        model.add_value('content', content.text)
        print(model)


if __name__ == '__main__':
    spider = MySpider()
