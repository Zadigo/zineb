from pydispatch import dispatcher
from pydispatch.dispatcher import disconnect, getAllReceivers, liveReceivers

from zineb.utils.general import create_logger


class Signal:
    def disconnect_all(self, sender, signal):
        for receiver in liveReceivers(getAllReceivers(sender, signal)):
            self.disconnect(receiver, signal=signal, sender=sender) 

    def receivers(self, sender):
        return getAllReceivers(sender=sender)

    def connect(self, receiver, signal=None, sender=None):
        """
        Connect a receiver to a sender

        Parameters
        ----------

            receiver (func)
                The function that is to receive the signal

            signal ([type], optional): [description]. Defaults to None.
            sender ([type], optional): [description]. Defaults to None.
        """
        if sender is None:
            sender = dispatcher.Any

        if signal is None:
            signal = dispatcher.Any
            
        dispatcher.connect(receiver, signal=signal, sender=sender)

    def disconnect(self, receiver, signal, sender):
        dispatcher.disconnect(receiver, signal=signal, sender=sender)

    def send(self, signal, sender, **kwargs):
        return dispatcher.send(signal, sender=sender, **kwargs)


signal = Signal()


# def register(sender, signal, name=None):
#     def _signal(func):
#         signal.connect(func, signal, name=name)
#         return dispatcher.send
#     return _signal


pre_start = signal
post_start = signal

pre_download = signal


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
