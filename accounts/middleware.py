"""
accounts/middleware.py - Custom middleware for user activity tracking
Django 5.x style
"""
import json
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest


class UserActivityMiddleware:
    """
    Django 5.x style middleware.
    Tracks user requests for analytics.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """
        Called on every request before view processing.
        """
        if request.user.is_authenticated:
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
        response = self.get_response(request)
        return response

    def _get_client_ip(self, request: HttpRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class UserActivityExceptionMiddleware:
    """
    Django 5.x style middleware.
    Tracks exceptions for analytics.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """
        Called on every request before view processing.
        """
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            if hasattr(request, 'user') and request.user.is_authenticated:
                from accounts.models import UserActivity
                UserActivity.objects.create(
                    user=request.user,
                    action='exception',
                    ip_address=self._get_client_ip(request),
                    metadata=json.dumps({'error': str(e), 'path': request.path})
                )
            raise e

    def _get_client_ip(self, request: HttpRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')