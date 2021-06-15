# class FieldTypes:
#     TEXT = 'TEXT'
#     INTEGER = 'INTEGER'
#     NULL = 'NULL'
#     BLOB = 'BLOB'
#     REAL = 'REAL'

class Field:
    pass


class CharField(Field):
    field_type = 'TEXT'


class IntegerField(Field):
    field_type = 'INTEGER'
