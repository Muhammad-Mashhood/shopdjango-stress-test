"""
notifications/views.py - Notification views
Depends on: notifications.models, accounts.models
"""
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')[:50]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read(request, pk):
    """Mark a notification as read."""
    try:
        notif = Notification.objects.get(pk=pk, user=request.user)
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save()
        return Response({'marked_read': True})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read for the user."""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    return Response({'marked_all_read': True})
