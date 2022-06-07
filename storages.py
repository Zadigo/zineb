import csv
import json
import os
import pathlib
from functools import lru_cache
from io import BytesIO

from PIL.Image import Image

from zineb.settings import settings


class FileDescriptor:
    def __init__(self): 
        self.buffer = BytesIO
        
    def __get__(self, instance, cls=None):
        self.open_file(instance)
        return self.buffer(self.__dict__['file_content'])

    def open_file(self, instance):
        with open(instance.full_path, mode='rb') as f:
            content = f.read()
            file_content = self.__dict__.get('file_content', None)
            if file_content is None:
                self.__dict__['file_content'] = content
    
        
class File:
    content = FileDescriptor()
    
    def __init__(self, full_path):
        self.name = full_path.stem
        self.verbose_name = full_path.name
        self.extension = self.verbose_name.split('.', maxsplit=1)[-1]
        self.size = full_path.stat().st_size
        self.full_path = full_path
        self.is_valid = full_path.exists() and full_path.is_file()
               
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
    
    def __eq__(self, value):
        return value == self.name
    
    def __hash__(self):
        return hash((self.name, self.size, self.extension))
    
    def __enter__(self, *args, **kwargs):
        return self
    
    def __exit__(self, *args, **kwargs):
        return False

    @classmethod
    def create(cls, full_path):
        return cls(full_path)
    
    def choose_parser(self, extension):
        extensions = {
            'json': json.load,
            'csv': csv.reader,
            'jpg': Image,
            'jpeg': Image,
            'png': Image,
            'svg': Image,
            'mp4': None
        }
        return extensions[extension]


class BaseStorage:
    def __init__(self):
        self.storage = None
        
    def prepare(self):
        pass
    
    def save(self, name, content=None):
        pass
    
    def open_file(self, name):
        f = self.get_file(name)
        parser = f.choose_parser(f.extension)
        return parser(f.content)
    
    def filename_generator(self, old_name):
        pass
    
    def path(self):
        pass
    
    def delete(self):
        pass
    
    def exists(self):
        pass
    
    def size(self):
        pass
        
        
class FileSystemStorage(BaseStorage):
    def __init__(self):
        super().__init__()
        self.storage_path = settings.MEDIA_FOLDER
        self.storage = self.load_files()
        self.files = []
        
    @lru_cache(maxsize=10)
    def load_files(self):
        items = []
        if self.storage_path is not None:
            items = list(os.walk(self.storage_path))                
        return items
    
    def prepare(self):
        files = self.load_files()
        for item in files:
            full_path, _, files = item
            
            for name in files:
                file_path = pathlib.Path(full_path).joinpath(name)
                instance = File.create(file_path)
                self.files.append((instance.name, instance))

    def get_file(self, name):
        instance = None
        for item in self.files:
            name, instance = item
            if name == instance:
                break
        return instance


class AWSFileSystemStorage(BaseStorage):
    pass
