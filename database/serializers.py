from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DaDatabases,DaMysqlConnection, DaMysqlSession

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class DaDatabasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DaDatabases
        fields = ['id','tb_type']

class DaMysqlConnectionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # nested or replace with just `user = serializers.PrimaryKeyRelatedField(...)` if needed
    db_type = DaDatabasesSerializer(read_only=True)  

    class Meta:
        model = DaMysqlConnection
        fields = [
            'id', 'db_type', 'user', 'host', 'password','db_user', 'db_name', 'port',
            'created_at', 'updated_at', 'active'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DaMysqlSessionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    connection = DaMysqlConnectionSerializer(read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = DaMysqlSession
        fields = [
            'session_id', 'connection', 'user',
            'created_at', 'updated_at', 'ttl_seconds',
            'active', 'is_expired'
        ]
        read_only_fields = ['session_id', 'created_at', 'updated_at', 'is_expired']

    def get_is_expired(self, obj):
        return obj.is_expired()
    
class MySQLQueryExecuteSerializer(serializers.Serializer):
    session_id = serializers.UUIDField(required=True)
    query = serializers.CharField(required=True)

    def validate_query(self, value):
        # Optional: basic check to prevent dangerous queries
        forbidden = ['DROP', 'DELETE', 'TRUNCATE', '--']
        upper_value = value.upper()
        if any(keyword in upper_value for keyword in forbidden):
            raise serializers.ValidationError("Query contains forbidden keywords.")
        return value