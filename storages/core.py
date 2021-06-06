import os
import warnings

import boto3
from zineb.settings import lazy_settings as global_settings
from zineb.storages.cache import StorageCache
from zineb.storages.storage_files import StorageFile


class Storage:
    storage_type = None
    
    def __init__(self):
        self._cache = StorageCache()

        media_folder = global_settings.MEDIA_FOLDER
        if self.storage_type == 'local':
            if media_folder is not None:
                files = os.listdir(media_folder)
                for file_path in files:
                    name, ext = os.path.basename(file_path).split('.')
                    self._cache.memory.setdefault(name, StorageFile(name, ext, file_path))
            else:
                warnings.warn("Note that the media folder root path "
                "was not found on your project.", stacklevel=1)

    def save_file(self, path_or_url):
        pass


class LocalStorage(Storage):
    storage_type = 'local'

    def __iter__(self):
        return iter(self.items())

    def __len__(self):
        return len(self.items())

    def __getitem__(self, name):
        return self._cache.memory.get(name)

    def __contains__(self, value):
        files = self._cache.get_files()
        truth_array = [value in file for file in files]
        return any(truth_array)

    def save_file(self, path_or_url):
        with open(path_or_url, mode='wb') as f:
            f.write()
            return StorageFile(f.name, f.name.split('.')[-1], path_or_url)


class AWSStorage(Storage):
    storage_type = 'web'

    def __init__(self):
        self.client = boto3.client('s3')
        
    def upload_file(self, path_or_url, bucket_name, file_name=None):
        file = self._cache.get(path_or_url)
        if os.path.isfile(file):
            self.client.upload_file(file.content, bucket_name, file_name)
