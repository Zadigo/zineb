from collections import deque


class Statistics:
    registry = deque()


class History(Statistics):
    def __call__(self, sender, signal, **kwargs):
        print(sender, signal, **kwargs)

