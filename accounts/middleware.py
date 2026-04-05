"""
accounts/middleware.py - Custom middleware for user activity tracking
Django 1.x middleware style (process_request/process_response methods)
"""
import json
from django.utils.translation import gettext_lazy as _


class UserActivityMiddleware(object):
    """
    Django 1.x style middleware (old-style class, not new MiddlewareMixin).
    Tracks user requests for analytics.
    """

    def process_request(self, request):
        """Called on every request before view processing."""
        if request.user.is_authenticated():
            from accounts.models import UserActivity
            # Only log API requests
            if request.path.startswith('/api/'):
                UserActivity.objects.create(
                    user=request.user,
                    action='api_request',
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    metadata=json.dumps({'path': request.path, 'method': request.method})
                )
        return None

    def process_response(self, request, response):
        """Called on every response."""
        return response

    def process_exception(self, request, exception):
        """Called when an exception is raised in a view."""
        if hasattr(request, 'user') and request.user.is_authenticated():
            from accounts.models import UserActivity
            UserActivity.objects.create(
                user=request.user,
                action='exception',
                ip_address=self._get_client_ip(request),
                metadata=json.dumps({'error': str(exception), 'path': request.path})
            )
        return None

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
