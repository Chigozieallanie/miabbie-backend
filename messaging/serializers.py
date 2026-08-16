from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'body', 'sender_is_admin', 'created_at']
        read_only_fields = ['id', 'sender_is_admin', 'created_at']