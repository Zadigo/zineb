import unittest
from zineb.storages import FileSystemStorage, AWSFileSystemStorage
from zineb.settings import settings
from pathlib import Path
import os

settings(MEDIA_FOLDER=Path('.').joinpath('test_project/media').absolute())


class TestStorage(unittest.TestCase):
    def test_file_system_storage(self):
        instance = FileSystemStorage()
        # self.assertTrue(len(list(instance.load_files())) > 0)


if __name__ == '__main__':
    unittest.main()
