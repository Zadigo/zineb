from threading import Thread

from zineb.http.request import HTTPRequest


class Pipeline:
    """
    Create a set of requests that will be treated
    continuously through a series of functions

    Note that once the HTTPRequest is created, it returns
    the original HTTP request object

    Pipeline's are useful for example when you wish to download
    a set of images at once

    Example
    -------
            def download_image(response):
                ...

            Pipeline([http://example.com], download_image)
    """

    def __init__(self, urls, *functions, **parameters):
        self.responses = []

        requests_to_send = []
        for i, url in enumerate(urls):
            request = HTTPRequest(url, index=i)
            request.options.update(**parameters)
            requests_to_send.append(request)

        types = []
        for function in functions:
            if type(function) == 'class':
                types.append(function)

        threads = []
        for request in requests_to_send:
            def wrapper():
                result = None
                request._send()
                response = request.html_response.cached_response
                self.responses.append(response)
                for function in functions:
                    # if type(function) == 'class':
                    #     # There are certain cases where
                    #     # the function that is passed turns
                    #     # out being a class. In that specific
                    #     # situation, maybe call the __call__
                    #     # method on that classe
                    #     instance = function(response)
                    #     instance()
                    # else:
                    if result is not None:
                        result = function(result)
                    else:
                        result = function(response)
            threads.append(Thread(target=wrapper))

        for thread in threads:
            thread.start()
            if thread.is_alive():
                thread.join()

        self.requests_to_send = requests_to_send

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

    def get(self, index):
        """
        Get an HTTPRequest object

        Parameters
        ----------

                index (int): the index of the item to get

        Returns
        -------

                type: resolved HTTPRequest object
        """
        try:
            return self.requests_to_send[index]
        except KeyError:
            return None
