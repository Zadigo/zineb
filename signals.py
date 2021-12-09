import weakref
from collections import defaultdict
from functools import partial, wraps
from typing import Any, Callable, Union

# from pydispatch.dispatcher import WEAKREF_TYPES

# {'some-sender': [222, 333, ...]}
CONNECTIONS = defaultdict(set)


# {111: {<func>222, ...}}
RECEIVERS = defaultdict(set)


def create_id(obj):
    return id(obj)


def name_if_object(obj: Union[type, Callable, str]):
    """Returns the object's name if it's a Type
    or a function"""
    if isinstance(obj, str):
        return obj

    types = ['type', 'function']
    if type(obj).__name__ in types:
        return obj.__name__.lower()
    return obj


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
    if isinstance(obj, (weakref.ReferenceType)):
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
    in the global 'all' scope"""
    receivers = set()
    receiver_ids = CONNECTIONS.get(name_if_object(sender), set())
    receiver_ids = receiver_ids.union(CONNECTIONS['all'])
    
    for receiver_id in receiver_ids:
        items = RECEIVERS[receiver_id]
        receivers = receivers.union(items)
    return [resolve_weak_reference(func) for func in receivers]


def connect(receiver, sender: Any = None, weak=True):
    receiver_id = create_id(receiver)

    if weak:
        def clean_up(old_func):
            for key, func in RECEIVERS.items():
                if old_func is func:
                    break
            try:
                CONNECTIONS.pop(key)
            except:
                pass

            try:
                RECEIVERS.pop(key)
            except:
                pass

        receiver = weakref.ref(receiver, clean_up)

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
        sender = 'all'

    # Check if sender is a string, a function
    # or a class and get the derived name
    # attrs = ['type', 'function']
    # if type(sender).__name__ in attrs:
    #     sender = sender.__name__.lower()
    sender = name_if_object(sender)

    connections = CONNECTIONS[sender]
    connections.add(receiver_id)


def disconnect(receiver: Any=None, sender: Any=None):
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
    return response


def receiver(sender, **kwargs):
    def wrapper(func):
        connect(func, sender=sender)
    return wrapper
