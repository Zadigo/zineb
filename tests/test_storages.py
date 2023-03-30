import os
import unittest
from pathlib import Path

from zineb.settings import settings
from zineb.storages import AWSFileSystemStorage, FileSystemStorage

settings(MEDIA_FOLDER=Path('.').joinpath('test_project/media').absolute())


class TestStorage(unittest.TestCase):
    def test_file_system_storage(self):
        instance = FileSystemStorage()
        # self.assertTrue(len(list(instance.load_files())) > 0)


if __name__ == '__main__':
    unittest.main()
