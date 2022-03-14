


INTERNAL_TYPES = ['null', 'integer', 'real', 'text', 'blob']

class BaseSchema:
    create_table = "CREATE TABLE {table} ({definitions})"
    alter_table = ""
    # create_column = "ALTER TABLE {table} ADD COLUMN {column} {definitions}"
    
    def __init__(self, connection):
        self.connection = connection
        
    @staticmethod
    def secure_value(value):
        if isinstance(value, str):
            pass
        elif isinstance(value, bool):
            return str(int(value))
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return f"X'{value.hex()}'"
        elif value is None:
            return 'NULL'
        
    @staticmethod
    def finalize_sql_statement(sql):
        if not sql.endswith(';'):
            return sql + ';'
        return sql
    
    def alter_table(self, model):
        pass
        
    def create_table_from_model(self, model):
        columns_to_create = []
        for name, field in model._meta.cached_fields.items():
            if field.internal_name == 'char':
                max_length = getattr(field, 'max_length')
                if max_length is None:
                    max_length = 50
                description = f"CHAR({max_length})"
            else:
                description = field.internal_name
            template = f"{name} {description.upper()}"

            default_value = getattr(field, 'default', None)
            if default_value is not None:
                template = template + f" DEFAULT {field.default}"

            allow_null = getattr(field, 'null', False)
            if not allow_null:
                template = template + f" NOT NULL"
            columns_to_create.append(template)

        columns_to_create.insert(0, 'ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL')
        definitions = ', '.join(columns_to_create)
        model_name = model._meta.model_name
        sql = self.create_table.format(table=model_name.lower(), definitions=definitions)

        self.execute(self.finalize_sql_statement(sql))
        
    def execute(self, sql, params=None):
        # with self.connection.cursor() as cursor:
        #     cursor.execute(sql, params)
        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()
        


class Schema(BaseSchema):
    pass
        
    # def __enter__(self):
    #     return self
    
    # def __exit__(self, exc_type, exc_value, traceback):
    #     return False
