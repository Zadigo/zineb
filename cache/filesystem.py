import glob
import pathlib
import pickle
import tempfile
import zlib
from hashlib import md5

from zineb.cache.base import BaseCache


class FileSystemCache(BaseCache):
    suffix = 'zcache'
    def __init__(self, directory):
        super().__init__()
        self.directory = pathlib.Path(directory).joinpath('cache').absolute()
    
    def _clean(self):
        # _cull
        pass
    
    def _list_cached_files(self):
        return [
            self.directory.joinpath(item) 
                for item in glob.glob1(self.directory, f"*.{self.suffix}")
        ]
    
    def _delete(self, filename):
        pass
        
    def _write_content(self, file, timeout, value):
        expiry = 300
        file.write(pickle.dumps(expiry, pickle.HIGHEST_PROTOCOL))
        file.write(zlib.compress(pickle.dumps(value, pickle.HIGHEST_PROTOCOL)))
        
    def _check_expiration(self, file):
        return False
    
    def add(self, key, value, timeout=300, version=None):
        self.create(key, value, timeout=timeout, version=version)
        
    def get(self, key, default=None, version=None):
        file_name = self.directory.joinpath('tmpc_imew52.zcache')
        with open(file_name, mode='rb') as f:
            if not self._check_expiration(file_name):
                return pickle.loads(zlib.decompress(f.read()))
        return default
        
    def create(self, key, value, timeout=300, version=None):
        filename = md5('somefilename'.encode('utf-8')).digest()
        self._clean()
        files = self._list_cached_files()
        number_of_items = len(files)
        for item in files:
            self._delete(item)
        d, path = tempfile.mkstemp(dir=self.directory)
        with open(d, mode='wb') as f:
            self._write_content(f, timeout, value)


f = FileSystemCache('.')
# f.create('easy_key', 'I love Kendall')
# print(f._list_cached_files())
print(f.get('google'))
