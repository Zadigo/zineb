from zineb.app import Zineb

class Spider(Zineb):
    start_urls = ['http://example.com']

    def start(self, response, **kwargs):
        link = response.html_page.find('a')
        print(link)

spider = Spider()
