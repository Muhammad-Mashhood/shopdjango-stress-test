"""
products/urls.py - URL patterns for products (Django 1.x)
"""
from django.conf.urls import url
from products import views

urlpatterns = [
    url(r'^$', views.ProductListView.as_view(), name='product-list'),
    url(r'^featured/$', views.featured_products, name='featured-products'),
    url(r'^categories/$', views.CategoryListView.as_view(), name='category-list'),
    url(r'^categories/(?P<slug>[\w-]+)/$', views.CategoryDetailView.as_view(), name='category-detail'),
    url(r'^brands/$', views.BrandListView.as_view(), name='brand-list'),
    url(r'^create/$', views.ProductCreateView.as_view(), name='product-create'),
    url(r'^(?P<slug>[\w-]+)/$', views.ProductDetailView.as_view(), name='product-detail'),
    url(r'^(?P<slug>[\w-]+)/update/$', views.ProductUpdateView.as_view(), name='product-update'),
    url(r'^(?P<product_id>\d+)/related/$', views.related_products, name='related-products'),
]
