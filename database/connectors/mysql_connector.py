# apps/database/connectors/mysql_connector.py
import pymysql
from pymysql.cursors import DictCursor

class MySQLConnector:
    def __init__(self, host, port, user, password, database, timeout=5):
        self.host = host
        self.port = int(port)
        self.user = user
        self.password = password
        self.database = database
        self.timeout = timeout
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=DictCursor,
                connect_timeout=self.timeout
            )
            print(f"MySQL DB connected successfully")
        except pymysql.MySQLError as e:
            raise ConnectionError(f"MySQL connection error: {str(e)}")

    def execute_query(self, query):
        if not self.connection:
            self.connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                if query.strip().lower().startswith("select"):
                    columns = [desc[0] for desc in cursor.description]
                    result = cursor.fetchall()
                    return {"columns": columns, "data": result}
                else:
                    self.connection.commit()
                    return {"affected_rows": cursor.rowcount}
        except Exception as e:
            raise RuntimeError(f"Query failed: {str(e)}")
        
    def list_tables(self):
        with self.connection.cursor() as cursor:
            # Step 1: Get all table names
            cursor.execute("SHOW TABLES;")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            
            table_data = []

            for table in tables:
                # Step 2: Get columns for the table
                cursor.execute(f"SHOW COLUMNS FROM `{table}`;")
                columns = [col['Field'] for col in cursor.fetchall()]

                # Step 3: Get row count
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM `{table}`;")
                    row_count = cursor.fetchone()['count']
                except:
                    row_count = 'N/A'  # In case of permissions or view

                table_data.append({
                    "table_name": table,
                    "columns_count": len(columns),
                    "row_count": row_count,
                })

        return table_data
    
    def get_full_db_schema(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = [list(row.values())[0] for row in cursor.fetchall()]
            
            lines = []

            for table in tables:
                # Get columns
                cursor.execute(f"""
                    SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_KEY
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """, (self.database, table))
                columns = cursor.fetchall()

                col_parts = []
                pk = []
                for col in columns:
                    col_parts.append(f"{col['COLUMN_NAME']}:{col['COLUMN_TYPE']}")
                    if col['COLUMN_KEY'] == 'PRI':
                        pk.append(col['COLUMN_NAME'])

                # Get foreign keys
                cursor.execute(f"""
                    SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                        AND REFERENCED_TABLE_NAME IS NOT NULL
                """, (self.database, table))
                fks = cursor.fetchall()
                fk_parts = [f"{fk['COLUMN_NAME']} → {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}" for fk in fks]

                line = f"Table: {table} ({', '.join(col_parts)}"
                if pk:
                    line += f", PK: {', '.join(pk)}"
                if fk_parts:
                    line += f", FK: {', '.join(fk_parts)}"
                line += ")"
                lines.append(line)

            return "\n".join(lines)


    def close(self):
        if self.connection:
            print(f"DB connection has been closed")
            self.connection.close()

    def __enter__(self):
        self.connect()
        return self 

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()