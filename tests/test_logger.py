import unittest

from zineb.logger import logger


class TestLogger(unittest.TestCase):
    def test_logging(self):
        # If not project is set, the logging
        # should happen at the root of Zineb
        logger.instance.info('Log from test!')


if __name__ == '__main__':
    unittest.main()
