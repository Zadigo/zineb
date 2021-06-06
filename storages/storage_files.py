import os
from io import BytesIO
from PIL.Image import Image


class StorageFile:
    def __init__(self, name, extension, path):
        self.name = name
        self.extension = extension
        if not os.path.exists(path):
            raise FileExistsError(f"File does not exist: {path}")
        self.path = path
        self.content = self.read_file()

    def __rerpr__(self):
        return f"<{self.__class__.__name__}(name={self.name})>"

    def __contains__(self, value):
        return any([value in self.name])

    def read_file(self):
        with open(self.path, mode='rb') as f:
            buffer = BytesIO(f.read())
        return buffer

    def write_file(self, to_path):
        with open(to_path, mode='wb') as f:
            f.write(self.content)

    def delete_file(self, is_local=True):
        if os.path.exists(self.path):
            os.remove(self.path)


class ImageFile(StorageFile):
    def __init__(self):
        super().__init__()
        self.image = Image.frombytes(self.content)
