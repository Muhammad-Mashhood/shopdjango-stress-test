from django.contrib import admin
from notifications.models import Notification, EmailLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__email', 'title')
    raw_id_fields = ('user',)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('recipient_email', 'subject')
    readonly_fields = ('created_at',)
