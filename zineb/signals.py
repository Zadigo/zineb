import inspect
import threading
import time
import weakref
from functools import lru_cache

NO_RECEIVERS = object()


@lru_cache(maxsize=512)
def get_function_parameters(func, remove_first):
    """Returns the callable parameters removing
    "self" from the parameters if the method is 
    a class method"""
    params = tuple(inspect.signature(func).parameters.values())
    return params[1:] if remove_first else params


def get_callable_parameters(func):
    """Checks whether func is class function
    or a normal function. Class functions need
    to be extracted using `__func__`"""
    result = inspect.ismethod(func)
    func = result.__func__ if result else func
    return get_function_parameters(func, remove_first=result)


def test_function_accept_kwargs(func):
    """Checks if a function accepts keyword arguments
    
    >>> def test_function(**kwargs):
    ...     pass
    ...
    ... result = get_function_parameters(test_function)
    ... True"""
    return any(item for item in get_callable_parameters(func) if item.kind == item.VAR_KEYWORD)


def make_id(item):
    """Get the current element's ID"""
    if hasattr(item, "__func__"):
        return (id(item.__self__), id(item.__func__))
    return id(item)


NONE_ID = make_id(None)


class Signal:
    """Base class for creating a signal by connecting
    a receiver to a sender function"""

    def __init__(self):
        self.receivers = []
        self.lock = threading.Lock()
        # self.sender_receivers_cache = weakref.WeakKeyDictionary() if use_caching else {}
        self.sender_receivers_cache = {}
        self._has_dead_receivers = False

    def _remove_receiver(self):
        self._has_dead_receivers = True

    def _clear_dead_receivers(self):
        # Note: caller is assumed to hold self.lock.
        if self._has_dead_receivers:
            self._has_dead_receivers = False
            self.receivers = [
                item for item in self.receivers
                if not (isinstance(item[1], weakref.ReferenceType) and item[1]() is None)
            ]

    def _live_receivers(self, sender):
        receivers = []

        if not receivers:
            with self.lock:
                self._clear_dead_receivers()
                incoming_sender_key = make_id(sender)
                for (receiver_key, sender_key), receiver in self.receivers:
                    if sender_key == NONE_ID or sender_key == incoming_sender_key:
                        receivers.append(receiver)

        non_weak_receivers = []

        for receiver in receivers:
            if isinstance(receiver, weakref.ReferenceType):
                # Dereference the weak reference.
                receiver = receiver()
                if receiver is not None:
                    non_weak_receivers.append(receiver)
            else:
                non_weak_receivers.append(receiver)
        return non_weak_receivers

    def has_listeners(self, sender=None):
        return bool(self._live_receivers(sender))

    def connect(self, receiver, sender=None, weak=True, uid=None):
        """Connect a receiver to a sender for a signal

        >>> signal = Signal()
        ...
        ... def my_receive_function(**kwargs):
        ...     pass
        ... 
        ... def my_send_function(**kwargs):
        ...     pass
        ...
        ... signal.connect(my_receive_function, sender=my_send_function)
        ... signal.send(my_send_function, a=1)"""
        if not callable(receiver):
            raise TypeError("A receiver should be a callable")

        if not test_function_accept_kwargs(receiver):
            raise TypeError("A receiver should receive keyword arguments")

        if uid is None:
            uid = make_id(receiver)
        # Create the tuple that links
        # the receiver to the sender
        key = (make_id(uid), make_id(sender))

        if weak:
            reference = weakref.ref
            receiver_object = receiver

            if hasattr(receiver, "__self__") and hasattr(receiver, "__func__"):
                reference = weakref.WeakMethod
                receiver_object = receiver.__self__

            receiver = reference(receiver)
            weakref.finalize(receiver_object, self._remove_receiver)

        with self.lock:
            self._clear_dead_receivers()
            if not any(r_key == key for r_key, _ in self.receivers):
                self.receivers.append((key, receiver))
            self.sender_receivers_cache.clear()

    def disconnect(self, receiver=None, sender=None, uid=None):
        """Disconnect a receiver from a sender"""
        if uid:
            lookup_key = (uid, make_id(sender))
        else:
            lookup_key = (make_id(receiver), make_id(sender))

        disconnected = False
        with self.lock:
            self._clear_dead_receivers()
            for i in range(len(self.receivers)):
                receiver_key, _ = self.receivers[i]
                if receiver_key == lookup_key:
                    del self.receivers[i]
                    disconnected = True
                    break
            self.sender_receivers_cache.clear()
        return disconnected

    def send(self, sender, **named):
        """
        Send signal from sender to all connected receivers.

        If any receiver raises an error, the error propagates back through send,
        terminating the dispatch loop. So it's possible that all receivers
        won't be called if an error is raised.
        """
        logic = [
            not self.receivers,
            self.sender_receivers_cache.get(sender) is NO_RECEIVERS
        ]

        if any(logic):
            return []

        return [
            (receiver, receiver(signal=self, sender=sender, **named))
            for receiver in self._live_receivers(sender)
        ]

    def send_to_all(self, sender, **named):
        logic = [
            not self.receivers,
            self.sender_receivers_cache.get(sender) is NO_RECEIVERS
        ]
        if not any(logic):
            return []

        responses = []
        for receiver in self._live_receivers(sender):
            try:
                response = receiver(signal=self, sender=sender, **named)
            except Exception as e:
                responses.append((receiver, e))
            else:
                responses.append((receiver, response))
        return responses


def function_to_receiver(signal, **kwargs):
    def decorator(func):
        if isinstance(signal, (list, tuple)):
            for item in signal:
                item.connect(func, **kwargs)
        else:
            signal.connect(func, **kwargs)
        return func
    return decorator
