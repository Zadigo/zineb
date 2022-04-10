DEBUG = 10
INFO = 20
WARNING = 30
ERROR = 40
CRITICAL = 50

class BaseMessage:
    def __init__(self, message, level, obj=None, **kwargs):
        self.message = message
        self.level = level
        self.obj = obj
        
    def __repr__(self):
        path = f"{self.obj.__module__}.{self.obj.__class__.__name__}"
        return f"<{self.__class__.__name__} for {path} [level={self.level}]>"


class ErrorMessage(BaseMessage):
    def __init__(self, message, *args, **kwargs):
        return super().__init__(message, DEBUG, *args, **kwargs)


class CriticalMessage(BaseMessage):
    def __init__(self, message, *args, **kwargs):
        return super().__init__(message, CRITICAL, *args, **kwargs)
