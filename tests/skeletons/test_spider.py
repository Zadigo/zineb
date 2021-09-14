import unittest


class BaseSpider(type):
    def __new__(cls, name, bases, attrs):
        return super().__new__(cls, name, bases, attrs)


class Spider(metaclass=BaseSpider):
    start_urls = []

    def __init__(self):
        for i in range(1, 10):
            self.start(i)

    def start(self, value):
        pass


class Zineb(Spider):
    pass


test_container = []


class CustomSpider(Zineb):
    def start(self, value):
        test_container.append(value)


c = CustomSpider()


class TestProcess(unittest.TestCase):
    def test_container(self):
        self.assertListEqual(test_container, [1, 2, 3, 4, 5, 6, 7, 8, 9])

if __name__ == '__main__':
    unittest.main()
