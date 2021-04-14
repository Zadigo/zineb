import asyncio
import warnings
from typing import Callable, Optional, Sequence, Union, Type
from warnings import warn
from zineb.models.datastructure import Model
from zineb.http.request import HTTPRequest
from zineb.http.responses import HTMLResponse, JsonResponse, XMLResponse



# class Pipeline:
#     def __init__(self):
#         self.errors = []

#     def _warn_user(self, message, using):
#         warnings.warn(message, UserWarning, stacklevel=6)


# class ResponsesPipeline(Pipeline):
#     """
#     Treats a set of HTTP Responses through a set of functions

#     This pipeline is ideal for working with multiple responses
#     at once in order to do something with them and do multiple 
#     things at a time with a same response

#     Example
#     -------

#         Suppose you have a set of urls that you want to request for
#         and get all the responses, in your start function you would
#         have something like this:
            
#             class MySpider(Zineb):
#                 start_urls = []

#                 def start(self, response, request=None, **kwargs):
#                     urls = [http://example.com, http://example.com]
#                     responses = request.follow_all(urls)
#                     RequestPipeline(responses, [self.do_something_with_each_response])

#                     # Continue my code here

#                 def do_something_with_each_response(self, response, **kwargs):
#                     link = response.html_page.find("a")

#         Once the class is completed, the code resumes normally.

#     Parameters
#     ----------

#             responses (list): a list of HTMLResponse objects (instances)
#             functions (list): a list of functions to call
#             parameters (dict): things you want to pass to each method called
#             options (dict): extra options for the class
#     """
#     def __init__(self, responses:list, functions:list, 
#                  parameters:dict={}, **options):
#         super().__init__()
#         self.responses = responses

#         types = []
#         for function in functions:
#             if type(function) == 'class':
#                 types.append(function)

#         results = []

#         async def coordinator(response):
#             for function in functions:
#                 if isinstance(response, HTTPRequest):
#                     if response.resolved:
#                         response = response._http_response
#                     else:
#                         self.errors.append(f"{response} is not resolved")

#                 try:
#                     result = function(
#                         response,
#                         soup=response.html_page,
#                         **parameters
#                     )
#                     # if parameters:
#                     # else:
#                     #     return await function(response)
#                 except Exception as e:
#                     print(e.args)
#                     # self.errors.append(f"An error occured within the Pipe. {e.args}")
#                     raise 
#                 else:
#                     if result is not None:
#                         return await result
#                 finally:
#                     if self.errors:
#                         for error in self.errors:
#                             self._warn_user(error, UserWarning)
        
#         async def main():
#             for response in responses:
#                 result = await coordinator(response)
#                 if result or result is not None:
#                     results.extend([result])

#         asyncio.run(main())

#     def __repr__(self):
#         return f"{self.__class__.__name__}({self.responses})"

#     def __str__(self):
#         return str(self.responses)
        

# class HTTPPipeline:
#     """
#     Create and send a set of requests that will be treated
#     continuously through a series of functions

#     Note that once the HTTPRequest is created, it returns
#     the original HTTP request object

#     Pipeline's are useful for example when you wish to download
#     a set of images at once

#     Example
#     -------
#             def download_image(response):
#                 ...

#             Pipeline([http://example.com], [download_image])
#     """

#     def __init__(self, urls:list, functions:list, 
#                  parameters: dict={}, **options):
#         self.responses = []
#         model = options.get('model')

#         requests_to_send = []
#         for i, url in enumerate(urls):
#             if isinstance(url, HTTPRequest):
#                 url = url.url
#             request = HTTPRequest(str(url), index=i)
#             request.options.update(**options)
#             requests_to_send.append(request)

#         types = []
#         for function in functions:
#             if type(function) == 'class':
#                 types.append(function)

#         results = []
#         async def run_function(func: Callable, result, new_parameters:dict):
#             # if not parameters:
#             #     return func(result)
#             return func(**new_parameters)

#         async def wrapper(request):
#             result = None
#             request._send()
#             response = request.html_response.cached_response
#             self.responses.append(response)

#             new_parameters = {
#                 **parameters,
#                 'response': request.html_response,
#                 'request': request,
#                 'soup': request.html_response.html_page,
#             }
            
#             for function in functions:
#                 return await run_function(function, result, new_parameters)
#                 # if result is not None:
#                 #     # result = function(result)
#                 #     result = await run_function(function, result)
#                 # else:
#                 #     if parameters:
#                 #         # result = function(result, **parameters)
#                 #         result = await run_function(function, result, **parameters)
#                 #     else:
#                 #         # result = function(response)
#                 #         result = await run_function(function, response)
#                 # return result

#         async def main():
#             for request in requests_to_send:
#                 # task = asyncio.create_task(wrapper(request))
#                 # await task
#                 await asyncio.sleep(1)
#                 result = await wrapper(request)
#                 if result and result is not None:
#                     results.append(result)
    
#         asyncio.run(main())
#         self.requests_to_send = requests_to_send
#         self.results = results

#     def __repr__(self):
#         return f"{self.__class__.__name__}({self.requests_to_send})"

#     def __str__(self):
#         return str(self.requests_to_send)

#     def __getitem__(self, index):
#         return self.requests_to_send[index]

#     def __iter__(self):
#         return iter(self.requests_to_send)

#     def __enter__(self):
#         return self.requests_to_send

#     def __exit__(self, exc_type, exc_val, exc_tb):
#         return False
        

class Callback:
    """
    The CallBack class allows you to run a callback function
    once each url is processed and passed through the main start 
    function of your spider.

    Parameters
    ----------
    
        request_or_url (Union[HTTPRequest, str]): [description]
        func (Callable[[Union[HTMLResponse, JsonResponse, XMLResponse], HTTPRequest, Optional[dict]], None]): [description]
        model (Type[Model], optional): [description]. Defaults to None.

    Raises
    ------

        TypeError: [description]
    """
    def __init__(self, request_or_url: Union[HTTPRequest, str], 
                 func: Callable[[Union[HTMLResponse, JsonResponse, XMLResponse], HTTPRequest, Optional[dict]], None], 
                 model: Type[Model]=None):
        if not callable(func):
            raise TypeError('Func should be a callable function')

        self.func = func
        self.model = model

        # TODO: Restructure this section
        request = request_or_url
        if isinstance(request_or_url, str):
            request = HTTPRequest(request_or_url)
        request._send()

        self.html = request.html_response
        self.request = request
        self._response = None

    def __call__(self, request_or_url, func):
        return self.__init__(request_or_url, func)

    def _run_function(self):
        kwargs = {'model': self.model}
        self.func(self._response, request=self.request, **kwargs)
