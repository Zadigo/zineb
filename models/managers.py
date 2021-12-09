from typing import Callable, Type
from zineb.settings import lazy_settings
from functools import cached_property

# try:
#     from googleapiclient.discovery import build
#     from google_auth_oauthlib.flow import InstalledAppFlow
#     from google.auth.transport.requests import Request
#     from google.oauth2.credentials import Credentials
# except:
#     raise ImportError(("Google API client is not available on your computer."
#                        "Please run pip install --upgrade google-api-python-client "
#                        "google-auth-httplib2 google-auth-oauthlib"))

# class BaseAPI:
#     def __init__(self, name: str, version: str, credentials: str = None):
#         if credentials is not None:
#             result = Credentials.from_authorized_user_file(
#                 credentials,
#                 lazy_settings.GOOGLE_SHEET_SCOPE
#             )
#         else:
#             result = Credentials.from_authorized_user_info(
#                 lazy_settings.GOOGLE_SHEET_CREDENTIALS,
#                 lazy_settings.GOOGLE_SHEET_SCOPE
#             )

#         if not result or result is None:
#             None

#         self.conn = build(name, version, credentials=result)

#     @cached_property
#     def get_connection(self):
#         return self.conn


# class GoogleSheets(BaseAPI):
#     def __init__(self, credentials: str = None):
#         super().__init__('sheets', 'v4', credentials=credentials)

#         self._default_manager = GoogleSheetManager.copy(self.get_connection.spreadsheets())

#     # def __quit__(self):
#     #     self.get_connection.close()





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


m = GoogleSheetManager.new_instance(model=None, api_instance=None)
