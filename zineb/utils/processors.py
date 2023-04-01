from functools import cached_property, partial


class UrlProcessor:
    def __init__(self, func, **kwargs):
        self.urls = []
        processor = partial(func, urls=self.urls)
        self.result = processor(**kwargs)

    @cached_property
    def get_result(self):
        return self.result

    def __call__(self, func, **kwargs):
        self.__init__(func, **kwargs)
