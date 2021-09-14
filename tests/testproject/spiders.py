from zineb.app import Zineb

# Create your spiders here

class MySpider(Zineb):
    start_urls = [
        'http://example.com'
    ]

    def start(self, response, request, **kwargs):
        print(response.find('a'))
