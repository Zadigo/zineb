import os
from io import BytesIO

from PIL.Image import Image


class StorageFile:
    content = None
    
    def __init__(self, name: str, extension: str, path: str):
        self.name = name
        self.extension = extension
        if not os.path.exists(path):
            raise FileExistsError(f"File does not exist: {path}")
        self.path = path

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name})>"

    def __contains__(self, value):
        return any([value in self.name])

    def __getattr__(self, name):
        if name == 'content':
            content = getattr(self, name)
            if content is None:
                self.content = self.read_file()
        return super().__getattr__(name)

    def read_file(self):
        with open(self.path, mode='rb') as f:
            buffer = BytesIO(f.read())
        return buffer

    def write_file(self, to_path: str):
        with open(to_path, mode='wb') as f:
            f.write(self.content)

    def delete_file(self, is_local: bool=True):
        if os.path.exists(self.path):
            os.remove(self.path)


class ImageFile(StorageFile):
    def __init__(self, name: str, extension: str, path: str):
        super().__init__(name, extension, path)
        self.image = Image.frombytes(self.content)
