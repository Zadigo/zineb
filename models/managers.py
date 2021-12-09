from typing import Callable, Type
from zineb.settings import lazy_settings
from functools import cached_property


class DefaultManager:
    def __init__(self, model):
        self.model = model
        
    @classmethod
    def new_instance(cls, **kwargs):
        instance = cls(**kwargs)
        return instance


class APIManager(DefaultManager):
    """
    Abstracts certain specific querying and
    saving functionnatlies for a given API
    """
    def __init__(self, api_instance: Callable, model: Type):
        self.api_instance = api_instance
        super().__init__(model)

    def __call__(self, api_instance):
        self.__init__(api_instance)

    @classmethod
    def copy(cls, api_instance):
        return cls(api_instance)


class GoogleSheetManager(APIManager):
    def values(self, name: str):
        pass

    def insert(self, name: str, range: str = None, cell: str = None):
        pass

    def update(self, name: str, range: str = None, cell: str = None):
        pass

    def create(self, title: str):
        attrs = {
            'properties': {
                'title': title
            }
        }
        return self.sheet.create(body=attrs, fields='spreadsheetId').execute()
