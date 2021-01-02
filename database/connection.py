import sqlite3
from collections import OrderedDict
from functools import cached_property

import psycopg2
from zineb.database.sql import SQL
from zineb.models.datastructure import Model
from zineb.settings import Settings
from zineb.signals import Signal, signal

pre_save = Signal()
post_save = Signal()

class Database(SQL):
    settings = Settings()

    def __init__(self):
        self.db_settings = self.settings.get('DATABASE')
        self.db_path = self.db_settings.get('path', None)
        self.connected = False
        pre_save.connect(self, 'Database.PreSave')
        post_save.connect(self, 'Database,PostSave')

    def __call__(self, sender, **kwargs):
        return self._connection()

    @cached_property
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        self.connected = True
        return conn, conn.cursor


class SQLite(Database):
    registry = OrderedDict

    def _create_table(self, model):
        if not isinstance(model, Model):
            raise TypeError('Model should be an instance of zineb.models.datastructure.Model')

        fields = model._meta.fields.copy()
        sql = super()._new_table('some_table', fields, schema='celebrity')
        conn, cursor = self._connection

        with conn as db:        
            try:
                cursor.execute(sql)
            except:
                return False
            else:
                db.commit()
                return True

    def _insert(self):
        db, cursor = self._connection
        sql = super()._insert_into('some_table', [], [])
        cursor.execute(sql, [])
        self.save(using=db)
        return cursor.lastrowid

    def save(self, commit=False, using=None):
        if using is not None:
            using.commit()


class PostGres(Database):
    @cached_property
    def _connection(self):
        name = self.db_settings.get('name', None)
        user = self.db.settings.get('user')
        password = self.db.settings.get('password')
        parameters = f"dbname={name} user={user} password={password}"
        try:
            conn = psycopg2.connect(parameters)
        except:
            raise ConnectionError('Could not connect to database')
        else:
            return conn, conn.cursor
