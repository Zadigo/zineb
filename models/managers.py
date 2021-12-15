from typing import Callable, Type
from zineb.settings import lazy_settings
from functools import cached_property


class DefaultManager:
    def __init__(self, model):
        self.model = model
        
    @classmethod
    def new_instance(cls, **params):
        instance = cls(**params)
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


class S3Manager(APIManager):
    def __init__(self, **params):
        try:
            from botocore import session
        except:
            raise ImportError("Could not import module botocore: pip install botocore")
        session = session.Session()
        attrs = {
            'aws_access_key_id': getattr(lazy_settings, 'AWS_ACCESS_KEY_ID'),
            'aws_secret_access_key': getattr(lazy_settings, 'AWS_SECRET_ACCESS_KEY'),
            'aws_session_token': getattr(lazy_settings, 'AWS_SESSION_TOKEN'),
            'endpoint_url': getattr(lazy_settings, 'AWS_ENDPOINT_URL'),
            'region_name': getattr(lazy_settings, 'AWS_REGION_NAME'),
            'use_ssl': getattr(lazy_settings, 'AWS_USE_SSL')
        }
        client = session.create_client('s3', **attrs)
        super().__init__(api_instance=client)
        
manager = S3Manager.new_instance()
