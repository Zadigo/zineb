import unittest
from zineb.signals import Signal, function_to_receiver

test_signal = Signal()


def test_function(**kwargs):
    return True


def test_function2(**kwargs):
    return True


@function_to_receiver(test_signal)
def decorated_signal(**kwargs):
    """Function that is not explicitly
    linked to a sender"""
    return True


class TestSignal(unittest.TestCase):
    def setUp(self):
        # Test with a function that is actuall
        # connected to a sender
        test_signal.connect(test_function, self)
        # Test with a function that is not
        # explicitly connected to a sender
        test_signal.connect(test_function2)

    def test_signal_completion(self):
        self.assertTrue(len(test_signal.receivers) > 0)
        self.assertIsInstance(test_signal.receivers, list)
        self.assertIsInstance(test_signal.receivers[0], tuple)
        self.assertFalse(test_signal._has_dead_receivers)

        items = test_signal.send(self)
        self.assertTrue(items[0][1])
        self.assertTrue(items[1][1])


if __name__ == '__main__':
    unittest.main()
