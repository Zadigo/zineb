from collections import defaultdict
import weakref

class Identifier:
    def __repr__(self):
        return f"<Identifier: {self.__class__.__name__}>"
    
    def __str__(self):
        return self.__class__.__name__.upper()
    
    
class Any(Identifier):
    pass


class Anonymous(Identifier):
    pass    


ANY = Any()

ANONYMOUS = Anonymous()


def create_id(target):
    try:
        method = target.__func__
    except:
        return id(target)
    else:
        klass = target.__self__
        return (id(klass), id(method))


class WeakMethod:
    instances = weakref.WeakValueDictionary()
        
    def __new__(cls, target, callback=None):
        keys = create_id(target)

        key = f"{keys[0]}{keys[1]}"
        current = cls.instances.get(key, None)
        if current is not None:
            return current
        else:
            instance = super().__new__(cls)
            
            instance._alive = True
            instance.weak_class = weakref.ref(target)
            instance.weak_method = weakref.ref(target.__self__)
            instance.name = type(target).__name__
            instance.method_name = target.__name__
            
            cls.instances[key] = instance
            return instance
        
    def __repr__(self):
        return f"<weakref of {self.name}: {self.method_name}>"
    
    def __eq__(self, obj):
        if isinstance(obj, WeakMethod):
            if not self._alive or not obj._alive:
                return self is obj
            return self.weak_method == obj.weak_method
        raise NotImplementedError('Cannot compare a and b')
    
    def __ne__(self, obj):
        if isinstance(obj, WeakMethod):
            if not self._alive or not obj._alive:
                return self is not obj
            return self.weak_method == obj.weak_method
        raise NotImplementedError('Cannot compare a and b')
    
    def __call__(self):
        weak_class = self.weak_class()
        if weak_class is None:
            return None
        return weak_class.__get__(weak_class)    
        
        
def create_weak_method(target, callback=None):
    return WeakMethod(target, callback=callback)
    
    
class Signal:
    receivers = defaultdict(set)
    senders = defaultdict(set)
    
    def connect(self, receiver, sender=ANY, weak=True, uid=None):
        if not callable(receiver):
            raise TypeError('Receivers should be callable')
        
        if uid is None:
            lookup_key = (create_id(receiver), create_id(sender))
        else:
            lookup_key = (uid, create_id(sender))

        initial_receiver = receiver
        if weak:
            weak_reference_builder = weakref.ref
            if hasattr(receiver, '__self__') and hasattr(receiver, '__func__'):
                weak_reference_builder = WeakMethod
                receiver = receiver.__self__
            receiver = weak_reference_builder(receiver)
            
        exists = any(map(lambda x: lookup_key in x, self.receivers))
        if not exists:
            self.receivers[lookup_key] = receiver
            
        def something():
            print('finished')
            
        weakref.finalize(initial_receiver, something)
                
    def send(self, sender=ANY, **named):
        return [
            (receiver, receiver()(signal=self, sender=sender, **named))
                for receiver in self.receivers.values()
        ]
            
            
# class A:
#     def test(self):
#         pass
    
    
# def some_function(*args, **kwargs):
#     print(args, kwargs)
    

# signals = Signal()
# signals.connect(some_function)
# # print(signals.receivers)
# # print(signals.receivers)
# signals.send(sender=A().test, message='I love Kendall')

signals = Signal()
