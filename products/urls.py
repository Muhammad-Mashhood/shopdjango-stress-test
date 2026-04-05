"""
products/urls.py - URL patterns for products (Django 1.x)
"""
from django.urls import re_path
from products import views

urlpatterns = [
    re_path(r'^$', views.ProductListView.as_view(), name='product-list'),
    re_path(r'^featured/$', views.featured_products, name='featured-products'),
    re_path(r'^categories/$', views.CategoryListView.as_view(), name='category-list'),
    re_path(r'^categories/(?P<slug>[\w-]+)/$', views.CategoryDetailView.as_view(), name='category-detail'),
    re_path(r'^brands/$', views.BrandListView.as_view(), name='brand-list'),
    re_path(r'^create/$', views.ProductCreateView.as_view(), name='product-create'),
    re_path(r'^(?P<slug>[\w-]+)/$', views.ProductDetailView.as_view(), name='product-detail'),
    re_path(r'^(?P<slug>[\w-]+)/update/$', views.ProductUpdateView.as_view(), name='product-update'),
    re_path(r'^(?P<product_id>\d+)/related/$', views.related_products, name='related-products'),
]
