import os

from zineb.settings import settings
from functools import cached_property


class FileStorage:
    def __init__(self, path_or_url, **kwargs):
        self._storage_path = path_or_url
        self.exists = True
        if not path_or_url.startswith('http') or not path_or_url.startswith('https'):
            self.exists = os.path.exists(path_or_url)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._storage_path}, exists={self.exists})"

    @cached_property
    def _map_files(self):
        root, dirs, files = list(os.walk(self._storage_path))[0]
        # Build each dirs full path
        dirs = self._build_full_path(root, dirs)
        for _dir in dirs:
            yield os.walk(_dir)

    def _build_full_path(self, root, dirs):
        return list(map(lambda p: os.path.join(root, p)), dirs)

    def find(self, name):
        # return self._map_files
        pass

    def check(self, name):
        return self._map_files
        

class LocalFileStorage(FileStorage):
    def __init__(self, path, **kwargs):
        super().__init__(path, **kwargs)

        self.files_paths = []
        try:
            base, dirs, files = list(os.walk(self._storage_path))
        except:
            base = dirs = files = []
        self.storage_files = map(lambda x: self.files_paths.append(os.path.join(base, x)), files)


class AWSFileStorage(FileStorage):
    def __init__(self, url, **kwargs):
        super().__init__(url, **kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._storage_path})"


class FileFinder:
    file_storages = []

    def __init__(self):
        # In case both settings are provided,
        # just merge both elements together
        root = settings.MEDIA_FOLDER

        self.file_storages.append(('local', LocalFileStorage(root)))

        if settings.AWS_STORAGE_URL is not None:
            params = {
                'url': settings.AWS_STORAGE_URL,
                'secret_key': settings.AWS_SECRET_KEY,
                'something_key': settings.AWS_SOMETHING_KEY
            }
            self.file_storages.extend([('aws', AWSFileStorage(**params))])

    def __repr__(self):
        return f'< {self.__class__.__name__} storages={len(self.file_storages)} >'

    def __iter__(self):
        return iter(self.file_storages)

    def get_storage(self, storage_type, instance_only=False):
        def iterator(items):
            if storage_type in items:
                return True
            return False
        return list(filter(iterator, self.file_storages))
# f = FileFinder()
# print(f.file_storages)
