from rest_framework import serializers
from notifications.models import Notification, EmailLog


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'notification_type', 'title', 'message', 'is_read',
                  'related_object_id', 'related_object_type', 'created_at', 'read_at')
