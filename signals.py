import weakref
from collections import defaultdict
from functools import partial, wraps
from typing import Any, Callable, Type, Union

# # {'some-sender': [222, 333, ...]}
# CONNECTIONS = defaultdict(set)


# # {111: {<func>222, ...}}
# RECEIVERS = defaultdict(set)


# def create_id(obj):
#     return id(obj)


# def name_if_object(obj: Union[type, Callable, str]):
#     """Returns the object's name if it's a Type
#     or a function"""
#     if isinstance(obj, str):
#         return obj

#     types = ['type', 'function']
#     if type(obj).__name__ in types:
#         return obj.__name__.lower()
#     return obj


# def remove_old(receiver_id):
#     def wrapper(obj):
#         receivers = RECEIVERS[receiver_id]
#         try:
#             receivers.remove(obj)
#         except:
#             pass
#     return wrapper


# def resolve_weak_reference(obj):
#     # Resolve the weakref of the receiver
#     # by returning the true function
#     if isinstance(obj, (weakref.ReferenceType)):
#         receiver = obj()
#         if receiver is not None:
#             return receiver
#     return obj


# def get_all_receivers():
#     for _, items in RECEIVERS.items():
#         for receiver in items:
#             yield list(resolve_weak_reference(receiver))[-1]


# def filtered_receivers(sender: str):
#     """Return receivers that are explicitely
#     linked to a sender including those binded
#     in the global 'all' scope"""
#     receivers = set()
#     receiver_ids = CONNECTIONS.get(name_if_object(sender), set())
#     receiver_ids = receiver_ids.union(CONNECTIONS['all'])
    
#     for receiver_id in receiver_ids:
#         items = RECEIVERS[receiver_id]
#         receivers = receivers.union(items)
#     return [resolve_weak_reference(func) for func in receivers]


# def connect(receiver, sender: Any = None, weak=True):
#     receiver_id = create_id(receiver)

#     if weak:
#         def clean_up(old_func):
#             for key, func in RECEIVERS.items():
#                 if old_func is func:
#                     break
#             try:
#                 CONNECTIONS.pop(key)
#             except:
#                 pass

#             try:
#                 RECEIVERS.pop(key)
#             except:
#                 pass

#         receiver = weakref.ref(receiver, clean_up)

#     receivers = RECEIVERS[receiver_id]
#     if receiver not in receivers:
#         receivers.add(receiver)
#     else:
#         try:
#             receivers.remove(receiver)
#         except KeyError:
#             # If the receiver does not exist,
#             # then just create it
#             pass
#         receivers.add(receiver)

#     if sender is None:
#         # If the sender is not explicitely named,
#         # link the receiver to the glabal sending
#         # scope called 'all'
#         sender = 'all'

#     # Check if sender is a string, a function
#     # or a class and get the derived name
#     # attrs = ['type', 'function']
#     # if type(sender).__name__ in attrs:
#     #     sender = sender.__name__.lower()
#     sender = name_if_object(sender)

#     connections = CONNECTIONS[sender]
#     connections.add(receiver_id)


# def disconnect(receiver: Any=None, sender: Any=None):
#     disconnected = False
#     if sender is not None:
#         del CONNECTIONS[sender]
#         disconnected = True

#     if receiver is not None:
#         del RECEIVERS[receiver]
#         disconnected = True

#     return disconnected


# def send(sender=None, signal=None, **named):
#     response = []
#     receivers = filtered_receivers(sender=sender)
#     for receiver in receivers:
#         method = partial(receiver, sender=sender)
#         response.append(method(**named))
#     return response


# def receiver(sender, **kwargs):
#     def wrapper(func):
#         connect(func, sender=sender)
#     return wrapper


class Signals:
    # Represents relationship that exists
    # between a sender and its receivers:
    # {'sender': [222, 333, ...]}
    CONNECTIONS = defaultdict(set)

    # Represnts the receiver id and
    # the function that receives
    # {111: {<func>222, ...}}
    RECEIVERS = defaultdict(set)

    @staticmethod
    def create_id(obj):
        return id(obj)

    @staticmethod
    def name_if_object(obj: Union[type, Callable, str]):
        """Returns the object's name if it's a Type
        or a function"""
        if isinstance(obj, str):
            return obj

        types = ['type', 'function']
        if type(obj).__name__ in types:
            return obj.__name__.lower()
        return obj

    def remove_old(self, receiver_id):
        def wrapper(obj):
            receivers = self.RECEIVERS[receiver_id]
            try:
                receivers.remove(obj)
            except:
                pass
        return wrapper

    def resolve_weak_reference(self, obj):
        # Resolve the weakref of the receiver
        # by returning the true function
        if isinstance(obj, (weakref.ReferenceType)):
            receiver = obj()
            if receiver is not None:
                return receiver
        return obj

    def get_all_receivers(self):
        for _, items in self.RECEIVERS.items():
            for receiver in items:
                yield list(self.resolve_weak_reference(receiver))[-1]

    def filtered_receivers(self, sender: str):
        """Return receivers that are explicitely
        linked to a sender including those binded
        in the global 'all' scope"""
        receivers = set()
        receiver_ids = self.CONNECTIONS.get(self.name_if_object(sender), set())
        receiver_ids = receiver_ids.union(self.CONNECTIONS['all'])

        for receiver_id in receiver_ids:
            items = self.RECEIVERS[receiver_id]
            receivers = receivers.union(items)
        return [self.resolve_weak_reference(func) for func in receivers]

    def connect(self, receiver: Callable, sender: Any=None, weak: bool=True):
        """Connect a function that receives (receiver) either to
        the global scope 'all' or to a specific sender"""
        receiver_id = self.create_id(receiver)

        if weak:
            def clean_up(old_func):
                for key, funcs in self.RECEIVERS.items():
                    for func in funcs:
                        if old_func is func:
                            break
                        print(old_func, func, old_func == func)
                try:
                    self.CONNECTIONS.pop(key)
                except:
                    pass

                try:
                    self.RECEIVERS.pop(key)
                except:
                    pass
            
            receiver = weakref.ref(receiver, clean_up)

        receivers = self.RECEIVERS[receiver_id]
        if receiver not in receivers:
            receivers.add(receiver)
        else:
            try:
                receivers.remove(receiver)
            except KeyError:
                # If the receiver does not exist,
                # then just create it
                pass
            receivers.add(receiver)

        if sender is None:
            # If the sender is not explicitely named,
            # link the receiver to the glabal sending
            # scope called 'all'
            sender = 'all'

        # Check if sender is a string, a function
        # or a class and get the derived name
        sender = self.name_if_object(sender)

        connections = self.CONNECTIONS[sender]
        connections.add(receiver_id)

    def disconnect(self, receiver: Any = None, sender: Any = None):
        disconnected = False
        if sender is not None:
            del self.CONNECTIONS[sender]
            disconnected = True

        if receiver is not None:
            del self.RECEIVERS[receiver]
            disconnected = True

        return disconnected

    def send(self, sender: Union[Callable, Type, str]=None, **named):
        """Send data or a signal to the receiving functions
        in the global scope 'all' or to a specific sender"""
        receivers = self.filtered_receivers(sender=sender)
        # print(receivers)
        for receiver in receivers:
            method = partial(receiver, sender=sender)
            method(**named)

    def receiver(self, sender: Union[Any, Type, Callable, str]='all', **kwargs):
        """A decorator used to transform a function
        into a receiver
        
        Example
        -------

            @receiver(ExampleSender)
            def example_function(sender=None, **kwargs):
                pass
        """
        def wrapper(func):
            self.connect(func, sender=sender)
        return wrapper
    
signals = Signals()
