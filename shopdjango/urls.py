"""
ShopDjango URL Configuration - Django 1.x style
"""
from django.urls import re_path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api/accounts/', include('accounts.urls', namespace='accounts')),
    re_path(r'^api/products/', include('products.urls', namespace='products')),
    re_path(r'^api/orders/', include('orders.urls', namespace='orders')),
    re_path(r'^api/inventory/', include('inventory.urls', namespace='inventory')),
    re_path(r'^api/payments/', include('payments.urls', namespace='payments')),
    re_path(r'^api/reviews/', include('reviews.urls', namespace='reviews')),
    re_path(r'^api/shipping/', include('shipping.urls', namespace='shipping')),
    re_path(r'^api/discounts/', include('discounts.urls', namespace='discounts')),
    re_path(r'^api/notifications/', include('notifications.urls', namespace='notifications')),
    re_path(r'^api/analytics/', include('analytics.urls', namespace='analytics')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
