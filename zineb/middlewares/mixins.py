class MiddlewareMixin:
    def __call__(self, request):
        return request

    def process_middleware(self):
        pass
