import copy
import operator


def create_proxy_function(func):
    def inner(self, *args, **kwargs):
        if self.cached_object is None:
            self._init_object()
        return func(self.cached_object, *args, **kwargs)
    return inner


class LazyObject:
    cached_object = None
    
    # def __init__(self):
    #     self.cached_object = None

    def __getattr__(self, name):
        if self.cached_object is None:
            self._init_object()
        return getattr(self.cached_object, name)

    def __setattr__(self, name, value):
        if name == 'cached_object':
            self.__dict__['cached_object'] = value
            
        if self.cached_object is None:
            self._init_object()
        
        setattr(self.cached_object, name, value)

    def __delattr__(self, name):
        if self.cached_object is None:
            self._init_object()
        delattr(self.cached_object, name)

    def __copy__(self):
        if self.cached_object is None:
            return type(self)()
        return copy.copy(self.cached_object)

    def __call__(self, **kwargs):
        if self.cached_object is None:
            self._init_object()
        self.cached_object(**kwargs)
        return self.cached_object

    __dir__ = create_proxy_function(dir)
    __str__ = create_proxy_function(str)
    __repr__ = create_proxy_function(repr)
    __getitem__ = create_proxy_function(operator.getitem)
    __setitem__ = create_proxy_function(operator.setitem)

    def _init_object(self):
        """
        Use this class to implement the element that
        should stored in the cached_object attribute
        """
        
        
# class cached_property:
#     def __init__(self, func):
#         self.initial_func = func
#         self.__doc__ = getattr(func, '__doc__')
        
#     def __get__(self, instance, cls=None):
#         if instance is None:
#             return self
#         result = instance.__dict__['cache'] = self.initial_func(instance)
#         return result
