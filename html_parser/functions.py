from typing import Callable

class Function:
    def __init__(self, name: str, attrs: dict = {}):
        # if not isinstance(tag, BaseTag):
        #     raise ValueError('Requires tag')
        self.tag_name = name
        self.tag_attrs = attrs

    def resolve(self):
        raise NotImplementedError('bla bla bla')


class Lower(Function):
    def resolve(self, tag: Callable):
        result = self.tag.string
        return result.lower()
