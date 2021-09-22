# from collections import defaultdict
# from typing import Any, Callable, Dict, Union
# from pydispatch import dispatcher
# from pydispatch.dispatcher import disconnect, getAllReceivers, liveReceivers
# import weakref

# class Signal:
#     custom_signals = {}

#     def disconnect_all(self, sender, signal):
#         for receiver in liveReceivers(getAllReceivers(sender, signal)):
#             self.disconnect(receiver, signal=signal, sender=sender) 

#     def receivers(self, sender=dispatcher.Any, signal=dispatcher.Any):
#         return getAllReceivers(sender=sender, signal=signal)

#     def connect(self, receiver, signal=None, sender=None):
#         if signal is None:
#             signal = dispatcher.Any

#         if sender is None:
#             sender = dispatcher.Any

#         dispatcher.connect(receiver, signal=signal, sender=sender)

#     def disconnect(self, receiver, signal, sender):
#         dispatcher.disconnect(receiver, signal=signal, sender=sender)

#     def send(self, signal, sender, *arguments, **named):
#         return dispatcher.send(signal=signal, sender=sender, *arguments, **named)

#     def register(self, receiver: Callable[[str, Union[Dict, None]], None], tag: str=None):
#         if tag is None:
#             tag = receiver.__name__
#         self.custom_signals[tag] = receiver
#         self.connect(receiver)


# signal = Signal()


# def receiver(tag: str=None):
#     """
#     Connect a receiving function to the global
#     signals interface

#     Example
#     -------

#             @receiver(tag="tag")
#             def my_custom_function():
#                 # Do something here
#                 pass

#     Args:
#         tag (str, optional): [description]. Defaults to None.
#     """
#     def wrapper(func):
#         signal.register(func, tag=tag)
#     return wrapper


import weakref
from collections import defaultdict
from functools import partial, wraps
from typing import Any

from pydispatch.dispatcher import WEAKREF_TYPES

# {'some-sender': [222, 333, ...]}
CONNECTIONS = defaultdict(set)


# {111: {<func>222, ...}}
RECEIVERS = defaultdict(set)


def create_id(obj):
    return id(obj)


def remove_old(receiver_id):
    def wrapper(obj):
        receivers = RECEIVERS[receiver_id]
        try:
            receivers.remove(obj)
        except:
            pass
    return wrapper


def resolve_weak_reference(obj):
    # Resolve the weakref of the receiver
    # by returning the true function
    if isinstance(obj, WEAKREF_TYPES):
        receiver = obj()
        if receiver is not None:
            return receiver
    return obj


def get_all_receivers():
    for _, items in RECEIVERS.items():
        for receiver in items:
            yield list(resolve_weak_reference(receiver))[-1]


def filtered_receivers(sender: str):
    """Return receivers that are explicitely
    linked to a sender including those binded
    in the globall 'all' scope"""
    receivers = set()
    receiver_ids = CONNECTIONS[sender]
    receiver_ids = receiver_ids.union(CONNECTIONS['all'])
    for receiver_id in receiver_ids:
        items = RECEIVERS[receiver_id]
        receivers = receivers.union(items)

    # for func in receivers:
    #     return resolve_weak_reference(func)
    return [resolve_weak_reference(func) for func in receivers]


def connect(receiver, sender: Any = None, weak=True):
    receiver_id = create_id(receiver)

    if weak:
        receiver = weakref.ref(receiver, None)

    receivers = RECEIVERS[receiver_id]
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
        # sender_id = create_id(sender)
        sender = 'all'

    # Check if sender is a string, a function
    # or a class and get the derived name
    attrs = ['type', 'function']
    if type(sender).__name__ in attrs:
        sender = sender.__name__.lower()

    connections = CONNECTIONS[sender]
    connections.add(receiver_id)


def disconnect(receiver: Any = None, sender: Any = None):
    disconnected = False
    if sender is not None:
        del CONNECTIONS[sender]
        disconnected = True

    if receiver is not None:
        del RECEIVERS[receiver]
        disconnected = True

    return disconnected


def send(sender=None, signal=None, **named):
    response = []
    receivers = filtered_receivers(sender=sender)
    for receiver in receivers:
        method = partial(receiver, sender=sender)
        response.append(method(**named))
        # try:
        # except:
        #     pass
    return response


def receiver(sender, **kwargs):
    def wrapper(func):
        connect(func, sender=sender)
    return wrapper
