"""
ShopDjango URL Configuration - Django 1.x style
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^api/products/', include('products.urls', namespace='products')),
    url(r'^api/orders/', include('orders.urls', namespace='orders')),
    url(r'^api/inventory/', include('inventory.urls', namespace='inventory')),
    url(r'^api/payments/', include('payments.urls', namespace='payments')),
    url(r'^api/reviews/', include('reviews.urls', namespace='reviews')),
    url(r'^api/shipping/', include('shipping.urls', namespace='shipping')),
    url(r'^api/discounts/', include('discounts.urls', namespace='discounts')),
    url(r'^api/notifications/', include('notifications.urls', namespace='notifications')),
    url(r'^api/analytics/', include('analytics.urls', namespace='analytics')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
