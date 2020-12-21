from pydispatch import dispatcher
from pydispatch.dispatcher import disconnect, getAllReceivers, liveReceivers

from zineb.utils.general import create_logger


class Signal:
    def __init__(self) -> None:
        self.logger = create_logger(self.__class__.__name__)

    @staticmethod
    def disconnect_all(self, sender, signal):
        for receiver in liveReceivers(getAllReceivers(sender, signal)):
            disconnect(receiver, signal=signal, sender=sender) 

    def connect(self, receiver, signal, **kwargs):
        sender = kwargs.get('sender', dispatcher.Any)
        return dispatcher.connect(receiver, signal=signal, sender=sender, **kwargs)

    def disconnect(self, receiver, signal, **kwargs):
        return dispatcher.disconnect(receiver, signal=signal, **kwargs)

    def send(self, signal, sender, **kwargs):
        return dispatcher.send(signal, sender=sender, **kwargs)


signal = Signal()


def register(sender, signal, name=None):
    def _signal(func):
        signal.connect(func, signal, name=name)
        return dispatcher.send
    return _signal


pre_start = signal
post_start = signal

pre_download = signal

pre_save = signal
post_save = signal

pre_request = signal
post_request = signal

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
