"""
Represents the very basic flow of the value from
the internet to the container that holds the data

The expected result is that each container should
have their own unique values
"""

import random
import unittest


class DataContainer:
    def __init__(self):
        self.items = []

    def add_value(self, value):
        self.items.append(value)

    @classmethod
    def as_class(cls):
        instance = cls()
        return instance


class Base(type):
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)


class DataStructure(metaclass=Base):
    def __init__(self):
        self._cached_result = DataContainer.as_class()

    def __str__(self):
        return str(self._cached_result.items)

    def __eq__(self, values):
        return self._cached_result.items == values

    def _add_value(self, value):
        self._cached_result.add_value(value)


class Model(DataStructure):
    pass


class Model1(Model):
    pass


class Model2(Model):
    pass


a = Model1()
b = Model2()


for _ in range(5):
    a._add_value(random.randint(1, 10))
    b._add_value(random.randint(11, 20))


class TestProcess(unittest.TestCase):
    def test_containers_are_not_equal(self):
        self.assertFalse(a == b)


if __name__ == '__main__':
    unittest.main()
