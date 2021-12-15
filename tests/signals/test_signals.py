import unittest
from zineb.signals import signals
import weakref

class TestSignal(unittest.TestCase):
    def test_can_connect(self):
        def some_function(*args, **kwargs):
            print('some_function', args, kwargs)

        def some_function1(*args, **kwargs):
            print('some_function1', args, kwargs)
            
        signals.connect(some_function)
        signals.connect(some_function1, sender='SomeSender')
        
        self.assertEqual(len(signals.RECEIVERS), 2)
        # The global scope 'all' should only have
        # one single function 'some_function'
        self.assertEqual(len(signals.CONNECTIONS['all']), 1)
        self.assertEqual(len(signals.CONNECTIONS['SomeSender']), 1)
        
    def test_can_send(self):
        def some_function(*args, **kwargs):
            print('some_function', args, kwargs)
        signals.connect(some_function)
        signals.send(msg='Great message')


if __name__ == '__main__':
    unittest.main() 
        
        
#     def test_can_decorate(self):
#         @signals.receiver()
# def another_function(**kwargs):
#     print('another_function', kwargs)


# signals.connect(some_function)
# signals.connect(some_function1, sender='Google')
# signals.send(name='Kendall', sender='Google')
# # signals.disconnect('some_function')
