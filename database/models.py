import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import  timezone
from datetime import timedelta

# Create your models here.
class DaDatabases(models.Model):
    db_type = models.CharField(max_length=50, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)  # when created
    updated_at = models.DateTimeField(auto_now=True)      # on update
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "da_databases"

    def __str__(self):
        return self.db_type


class DaMysqlConnection(models.Model):
    db_type = models.ForeignKey(DaDatabases, on_delete=models.CASCADE, related_name='connections',default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mysql_connections')
    host = models.CharField(max_length=255, blank=False, null=False)
    password = models.CharField(max_length=128, blank=True, null=True)
    db_name = models.CharField(max_length=100, blank=False, null=False)
    db_user = models.CharField(max_length=100, blank=False, null=False)
    port = models.IntegerField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "da_mysql_connection"

    def __str__(self):
        return f"{self.db_name}@{self.host}"


class DaMysqlSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(DaMysqlConnection, on_delete=models.CASCADE, related_name='sessions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mysql_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ttl_seconds = models.PositiveIntegerField(default=18000)  # 30 minutes TTL
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "da_mysql_session"

    def is_expired(self):
        """
        Check if the session has expired based on the TTL value.
        """
        return timezone.now() > self.created_at + timedelta(seconds=self.ttl_seconds)

    def __str__(self):
        return str(self.session_id)