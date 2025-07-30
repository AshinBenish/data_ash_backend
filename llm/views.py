from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import DbChatService
from .serializer import SQLQueryRequestSerializer

# Create your views here.
class DbChatRecommendedQuery(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id") or request.COOKIES.get("db_session_id")

        if not session_id:
            return Response({"error": "Missing session_id"}, status=400)

        try:
            service = DbChatService(session_id=session_id, user=request.user)
            tables = service.get_recommend_query()
            return Response(tables)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class DbChatMySQL(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SQLQueryRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = serializer.validated_data["session_id"]
        query_question = serializer.validated_data["query_question"]
        
        try:
            service = DbChatService(session_id=session_id, user=request.user)
            tables = service.get_mysql_query(query_question)
            return Response(tables)
        except Exception as e:
            return Response({"error": str(e)}, status=500)