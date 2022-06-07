from asgiref.sync import sync_to_async

class BaseCache:
    def __init__(self):
        self.default_timeout = 300
        self.max_entries = 1
        self.key_prefix = ''
        self.version = 1
        
    def create_key(self, key, version=None):
        if version is None:
            version = self.version
        key = 'something'
        result = f"{self.key_prefix}:{self.version}:{key}"
        return result
    
    def add(self, key, value, timeout=300, version=None):
        pass
    
    async def async_add(self, key, value, timeout=300, version=None):
        return sync_to_async(self.add)(key, value, timeout, version)
        
