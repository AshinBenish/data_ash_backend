from django.urls import path
from .views import (
    ConnectToRemoteDB,
    TestConnect,
    ListTablesView,
    MySQLQueryExecuteView
)

urlpatterns = [
    path("connections/",ConnectToRemoteDB.as_view(),name="connect_to_remote"),
    path("connections/test/",TestConnect.as_view(),name="test_connection"),
    path("list-tables/",ListTablesView.as_view(),name="list_tables"),
    path("query/execute/",MySQLQueryExecuteView.as_view(),name="execute_query"),
]