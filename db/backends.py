import sqlite3
from functools import cached_property


class SQliteBackend:
    def __init__(self, name: str):
        self.connection = sqlite3.connect(name)

    @cached_property
    def get_cursor(self):
        return self.connection.cursor


class PostGresBackend:
    pass
