try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except:
    raise ImportError(("Google API client is not available on your computer."
                       "Please run pip install --upgrade google-api-python-client "
                       "google-auth-httplib2 google-auth-oauthlib"))

class BaseAPI:
    def __init__(self, name: str, version: str, credentials: str = None):
        if credentials is not None:
            result = Credentials.from_authorized_user_file(
                credentials,
                lazy_settings.GOOGLE_SHEET_SCOPE
            )
        else:
            result = Credentials.from_authorized_user_info(
                lazy_settings.GOOGLE_SHEET_CREDENTIALS,
                lazy_settings.GOOGLE_SHEET_SCOPE
            )

        if not result or result is None:
            None

        self.conn = build(name, version, credentials=result)

    @cached_property
    def get_connection(self):
        return self.conn


class GoogleSheets(BaseAPI):
    def __init__(self, credentials: str = None):
        super().__init__('sheets', 'v4', credentials=credentials)

    # def __quit__(self):
    #     self.get_connection.close()
