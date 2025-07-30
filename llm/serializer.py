from rest_framework import serializers

class SQLQueryRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField(required=True)
    query_question = serializers.CharField(required=True, max_length=300)