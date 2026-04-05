"""
accounts/urls.py - URL patterns for accounts app (Django 1.x url() style)
"""
from django.conf.urls import url
from accounts import views

urlpatterns = [
    url(r'^register/$', views.UserRegistrationView.as_view(), name='register'),
    url(r'^login/$', views.UserLoginView.as_view(), name='login'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='logout'),
    url(r'^profile/$', views.UserProfileView.as_view(), name='profile'),
    url(r'^change-password/$', views.change_password, name='change-password'),
    url(r'^verify/(?P<token>[a-f0-9]{64})/$', views.verify_email, name='verify-email'),
    url(r'^addresses/$', views.AddressListCreateView.as_view(), name='address-list'),
    url(r'^addresses/(?P<pk>\d+)/$', views.AddressDetailView.as_view(), name='address-detail'),
    url(r'^activity/$', views.UserActivityListView.as_view(), name='activity'),
]
