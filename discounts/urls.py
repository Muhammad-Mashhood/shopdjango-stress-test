from django.urls import re_path
from discounts import views

urlpatterns = [
    re_path(r'^$', views.DiscountListView.as_view(), name='discount-list'),
    re_path(r'^validate/$', views.validate_discount, name='discount-validate'),
    re_path(r'^(?P<pk>\d+)/$', views.DiscountDetailView.as_view(), name='discount-detail'),
]
