class Interface:
    """
    An Interface is a class that abstracts certain
    specific functionnatlies on a given API
    """
    def __init__(self, sheet):
        self.sheet = sheet

    def __call__(self, sheet):
        self.__init__(sheet)

    @classmethod
    def copy(cls, sheet_instance):
        return cls(sheet_instance)


class SheetManager(Interface):
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
