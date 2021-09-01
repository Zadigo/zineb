import json
from collections import OrderedDict
from io import FileIO
from zineb.http.request import HTMLResponse

class WireFrame:
    """
    This middleware traces the path the crawler
    follows in order to get data on the web page
    """
    frame = OrderedDict()

    def __init__(self, response: HTMLResponse=None, limit: str='body'):
        if not isinstance(response, HTMLResponse):
            raise TypeError('Response should be an instance of zineb.response.HTMLResponse')
        buffer = FileIO('wireframe.json', mode='r+')
        loaded_data = json.load(buffer)
        data = loaded_data.copy()
        self.buffer = buffer

        self.wireframe = data
        self._response = response
        self.limit = limit

    def __exit__(self):
        self.buffer.close()

    def __call__(self, response: HTMLResponse, limit: str='body'):
        self.__init__(response, limit=limit)
        return self.frame

    def add_item(self, tag_name: str=None, attrs: dict={}):
        tag = self.response.find(tag_name, attrs=attrs)
        parents = list(tag.parents)
        for parent in parents:
            if parent.name == self.limit:
                break
            self.frame.setdefault(parent.name, parent.attrs)
            yield parent.name, parent.attrs
