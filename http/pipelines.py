import asyncio
from warnings import warn

from zineb.exceptions import PipelineError
from zineb.http.request import HTTPRequest


class Pipeline:
    def __init__(self):
        self.errors = []

    def _warn_user(self, using, message):
        warn(message, UserWarning)

class ResponsesPipeline(Pipeline):
    """
    Treats a set of HTTP Responses that will be
    treated continuously through a set of functions
    """
    def __init__(self, responses:list, functions:list, 
                 parameters:dict={}, **options):
        super().__init__()
        self.responses = responses

        types = []
        for function in functions:
            if type(function) == 'class':
                types.append(function)

        results = []

        async def coordinator(response):
            for function in functions:
                if isinstance(response, HTTPRequest):
                    if response.resolved:
                        response = response._http_response
                    else:
                        self.errors.append(f'{response} is not resolved')

                try:
                    if parameters:
                        return await function(response, **parameters)
                    else:
                        return await function(response)
                except:
                    self.errors.append(
                        PipelineError(function, response)
                    )
                finally:
                    if self.errors:
                        for error in self.errors:
                            self._warn_user(error, f'{function}, {response}')
        
        async def main():
            for response in responses:
                result = await coordinator(response)
                if result or result is not None:
                    results.extend([result])

        asyncio.run(main())

    def __repr__(self):
        return f"{self.__class__.__name__}({self.responses})"

    def __str__(self):
        return str(self.responses)
        

class HTTPPipeline:
    """
    Create and send a set of requests that will be treated
    continuously through a series of functions

    Note that once the HTTPRequest is created, it returns
    the original HTTP request object

    Pipeline's are useful for example when you wish to download
    a set of images at once

    Example
    -------
            def download_image(response):
                ...

            Pipeline([http://example.com], [download_image])
    """

    def __init__(self, urls:list, functions:list, 
                 parameters: dict={}, **options):
        self.responses = []

        requests_to_send = []
        for i, url in enumerate(urls):
            if isinstance(url, HTTPRequest):
                url = url.url
            request = HTTPRequest(str(url), index=i)
            request.options.update(**options)
            requests_to_send.append(request)

        types = []
        for function in functions:
            if type(function) == 'class':
                types.append(function)

        results = []
        async def run_function(func, result, **parameters):
            if not parameters:
                return func(result)
            return func(result, **parameters)

        async def wrapper(request):
            result = None
            request._send()
            response = request.html_response.cached_response
            self.responses.append(response)
            
            for function in functions:
                if result is not None:
                    # result = function(result)
                    result = await run_function(function, result)
                else:
                    if parameters:
                        # result = function(result, **parameters)
                        result = await run_function(function, result, **parameters)
                    else:
                        # result = function(response)
                        result = await run_function(function, response)
                return result

        async def main():
            for request in requests_to_send:
                # task = asyncio.create_task(wrapper(request))
                # await task
                await asyncio.sleep(1)
                result = await wrapper(request)
                if result and result is not None:
                    results.append(result)
    
        asyncio.run(main())
        self.requests_to_send = requests_to_send
        self.results = results

    def __repr__(self):
        return f"{self.__class__.__name__}({self.requests_to_send})"

    def __str__(self):
        return str(self.requests_to_send)

    def __getitem__(self, index):
        return self.requests_to_send[index]

    def __iter__(self):
        return iter(self.requests_to_send)

    def __enter__(self):
        return self.requests_to_send

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
        

class CallBack:
    def __init__(self, request_or_url, func):
        if not callable(func):
            raise TypeError('Func should be a callable function')
        self.func = func
        request = request_or_url
        if isinstance(request_or_url, str):
            request = HTTPRequest(request_or_url)

        request._send()
        self.html = request.html_response
        self.request = request

    def __call__(self, request_or_url, func):
        return self.__init__(request_or_url, func)

    def _run_function(self):
        self.func(self._response, request=self.request)
