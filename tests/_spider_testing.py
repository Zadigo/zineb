from zineb.app import Zineb

class Spider(Zineb):
    start_urls = ['http://example.com']
    
    def start(self, response, **kwargs):
        print(response.find('a'))

spider = Spider()
