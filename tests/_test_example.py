from zineb.app import Zineb


class Example(Zineb):
    start_urls = ['http://example.com']

    def start(self, response, **kwargs):
        # print(response, kwargs)
        pass

example = Example()
