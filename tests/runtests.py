import unittest


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    suite.addTest(TestCommands('test_create_spider'))
    runner.run(suite)
