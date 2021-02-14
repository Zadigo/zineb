import json
from collections import OrderedDict

class WireFrame:
    """
    This middleware traces the path the crawler
    follows in order to get  data on the web page
    """
    frame = OrderedDict()

    def __init__(self, response=None, limit='body'):
        with open('wireframe.json', mode='r') as f:
            loaded_data = json.load(f)
            data = loaded_data.copy()

        self.wireframe = data
        self.response = response
        self.limit = limit

    def __call__(self, response, limit='body'):
        self.__init__(response, limit=limit)
        return self.frame

    def add_item(self, tag_name, attrs):
        tag = self.response.find(tag_name, attrs=attrs)
        parents = list(tag.parents)
        for parent in parents:
            if parent.name == self.limit:
                break
            self.frame.setdefault(parent.name, parent.attrs)
            yield parent.name, parent.attrs
