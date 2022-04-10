import inspect
import unittest
from zineb.utils.functionnal import LazyObject

class MyLazyObject(LazyObject):
    def _init_object(self):
        self.cached_object = type('TestClass', (), {})


my_lazy_object = MyLazyObject()


class TestLazyObject(unittest.TestCase):
    def test_is_call(self):
        self.assertTrue(inspect.isclass(my_lazy_object()))
        
    


if __name__ == '__main__':
    unittest.main()
