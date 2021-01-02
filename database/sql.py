class SQL:
    SELECT = """SELECT {lhs} FROM {rhs};"""
    WHERE = """SELECT {lhs} FROM {rhs} WHERE {where_clause};"""
    INSERT = """INSERT INTO {lhs} VALUES({rhs});"""

    def _new_table(self, table_name, fields: list, **kwargs):
        fields = ' '.join(fields)
        sql = f"""
        CREATE TABLE IF NOT EXISTS {kwargs.get('schema')}.{table_name} (
            {fields}
        );
        """
        return sql

    def _insert_into(self, table_name, fields, values):
        number_of_values = len(values)
        placeholders = '?,' * number_of_values
        sql = f"""
        INSERT INTO {table_name}({fields}) VALUES({placeholders})
        """
        return sql

    def _select_from(self, table_name, fields):
        sql = f"""
        SELECT DISTINCT {fields}
        FROM {table_name};
        """
