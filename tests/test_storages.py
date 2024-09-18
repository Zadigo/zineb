import io
import unittest
from pathlib import Path

from zineb.settings import settings
from zineb.storages import AWSFileSystemStorage, FileSystemStorage, File

settings(MEDIA_FOLDER=Path('.').joinpath('tests/testproject/media').absolute())


class TestStorage(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = FileSystemStorage()

    def test_file_system_storage(self):
        self.assertIsNotNone(self.instance.storage_path)

        self.instance.prepare()
        file_object = self.instance.get_file('crawl')
        self.assertIsNotNone(file_object)
        self.assertIsInstance(file_object, File)

        self.assertIsInstance(file_object.content, io.BytesIO)


if __name__ == '__main__':
    unittest.main()
