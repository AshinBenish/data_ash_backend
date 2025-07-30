# apps/database/services/db_session_service.py
from database.models import DaMysqlSession,DaMysqlConnection
from database.connectors.mysql_connector import MySQLConnector
from django.core.exceptions import ObjectDoesNotExist

class DBSessionService:
    def __init__(self,user, session_id=None):
        self.session_id = session_id
        self.user = user

        if session_id:
            self.session:DaMysqlSession = self.get_session()

    def get_session(self):
        try:
            session = DaMysqlSession.objects.select_related("connection").get(session_id=self.session_id, user=self.user)
            if session.is_expired():
                raise PermissionError("Invalid or expired session")
            return session
        except ObjectDoesNotExist:
            raise PermissionError("Invalid or expired session")

    def get_connector(self):
        return MySQLConnector(
            host=self.session.connection.host,
            port=self.session.connection.port,
            user=self.session.connection.db_user,
            password=self.session.connection.password,
            database=self.session.connection.db_name
        )

    def run_query(self, query):
        connector = self.get_connector()
        try:
            connector.connect()
            result = connector.execute_query(query)
            return result
        finally:
            connector.close()

    def create_session(self,connection:DaMysqlConnection):
        return DaMysqlSession.objects.create(
            connection = connection,
            user = self.user
        )
    
    def list_tables(self):
        connector = self.get_connector()
        try:
            connector.connect()
            return connector.list_tables()
        finally:
            connector.close()

    def get_full_db_schema(self):
        connector = self.get_connector()
        try:
            connector.connect()
            return connector.get_full_db_schema()
        finally:
            connector.close()