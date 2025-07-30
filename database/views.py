from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import DaMysqlConnectionSerializer, MySQLQueryExecuteSerializer
from .connectors.mysql_connector import MySQLConnector
from .services.db_session_service import DBSessionService

# Create your views here.
class ConnectToRemoteDB(APIView):

    permission_classes = [IsAuthenticated] 

    def post(self,request):
        serializer = DaMysqlConnectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        with MySQLConnector(
                port=data['port'],
                host=data["host"],
                user=data["db_user"], 
                password=data["password"], 
                database=data["db_name"]
            ) as db:
            print(f"connected")

        connection = serializer.save(user=request.user)
        session = DBSessionService(user=request.user).create_session(connection=connection)
        return Response({'session_id': str(session.session_id)}, status=status.HTTP_201_CREATED)
    
class TestConnect(APIView):

    permission_classes = [IsAuthenticated] 

    def post(self,request):
        serializer = DaMysqlConnectionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            with MySQLConnector(
                    port=data['port'],
                    host=data["host"],
                    user=data["db_user"], 
                    password=data["password"], 
                    database=data["db_name"]
                ) as db:
                print(f"connected")

            connection = serializer.save(user=request.user)
            return Response({'status': "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status':'Failed','error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ListTablesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id") or request.COOKIES.get("db_session_id")

        if not session_id:
            return Response({"error": "Missing session_id"}, status=400)

        try:
            service = DBSessionService(session_id=session_id, user=request.user)
            tables = service.list_tables()
            return Response(tables)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class MySQLQueryExecuteView(APIView):

    permission_classes = [IsAuthenticated] 

    def post(self,request):
        serializer = MySQLQueryExecuteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            result = DBSessionService(
                session_id=data['session_id'], 
                user=request.user
            ).run_query(data['query'])
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status':'Failed','error' : str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        