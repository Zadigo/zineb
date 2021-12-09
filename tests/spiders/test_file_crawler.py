import os
import unittest

from zineb.tests.spiders.items import FileCrawler1, FileCrawler2, FileCrawler3


class TestFileCrawlers(unittest.TestCase):
    def test_with_root_folder(self):
        FileCrawler1()

    def test_without_start_files(self):
        FileCrawler2()

    def test_with_file_collector(self):
        FileCrawler3()


if __name__ == '__main__':
    unittest.main()
