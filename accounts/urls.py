"""
accounts/urls.py - URL patterns for accounts app (Django 1.x re_path() style)
"""
from django.urls import re_path
from accounts import views

urlpatterns = [
    re_path(r'^register/$', views.UserRegistrationView.as_view(), name='register'),
    re_path(r'^login/$', views.UserLoginView.as_view(), name='login'),
    re_path(r'^logout/$', views.UserLogoutView.as_view(), name='logout'),
    re_path(r'^profile/$', views.UserProfileView.as_view(), name='profile'),
    re_path(r'^change-password/$', views.change_password, name='change-password'),
    re_path(r'^verify/(?P<token>[a-f0-9]{64})/$', views.verify_email, name='verify-email'),
    re_path(r'^addresses/$', views.AddressListCreateView.as_view(), name='address-list'),
    re_path(r'^addresses/(?P<pk>\d+)/$', views.AddressDetailView.as_view(), name='address-detail'),
    re_path(r'^activity/$', views.UserActivityListView.as_view(), name='activity'),
]
