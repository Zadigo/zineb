from typing import Any, Callable, Dict, Union
from pydispatch import dispatcher
from pydispatch.dispatcher import disconnect, getAllReceivers, liveReceivers


class Signal:
    custom_signals = {}

    def disconnect_all(self, sender, signal):
        for receiver in liveReceivers(getAllReceivers(sender, signal)):
            self.disconnect(receiver, signal=signal, sender=sender) 

    def receivers(self, sender=dispatcher.Any, signal=dispatcher.Any):
        return getAllReceivers(sender=sender, signal=signal)

    def connect(self, receiver, signal=None, sender=None):
        if signal is None:
            signal = dispatcher.Any

        if sender is None:
            sender = dispatcher.Any

        dispatcher.connect(receiver, signal=signal, sender=sender)

    def disconnect(self, receiver, signal, sender):
        dispatcher.disconnect(receiver, signal=signal, sender=sender)

    def send(self, signal, sender, *arguments, **named):
        return dispatcher.send(signal=signal, sender=sender, *arguments, **named)

    def register(self, receiver: Callable[[str, Union[Dict, None]], None], tag: str=None):
        if tag is None:
            tag = receiver.__name__
        self.custom_signals[tag] = receiver
        self.connect(receiver)


signal = Signal()


def receiver(tag: str=None):
    """
    Connect a receiving function to the global
    signals interface

    Example
    -------

            @receiver(tag="tag")
            def my_custom_function():
                # Do something here
                pass

    Args:
        tag (str, optional): [description]. Defaults to None.
    """
    def wrapper(func):
        signal.register(func, tag=tag)
    return wrapper



# class A:
#     def create_order(self):
#         dispatcher.send(
#             signal='order.created',
#             sender=self,
#             order='Kendall'
#         )


# def send_order_email_listener(sender, order):
#     print(sender, order)
#     # print(f'[MAIL] sending email about order {sender}, {order}')


# dispatcher.connect(
#     send_order_email_listener,
#     signal='order.created',
#     sender=dispatcher.Any
# )


# w = A()
# w.create_order()
