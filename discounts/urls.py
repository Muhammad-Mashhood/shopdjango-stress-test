from django.conf.urls import url
from discounts import views

urlpatterns = [
    url(r'^$', views.DiscountListView.as_view(), name='discount-list'),
    url(r'^validate/$', views.validate_discount, name='discount-validate'),
    url(r'^(?P<pk>\d+)/$', views.DiscountDetailView.as_view(), name='discount-detail'),
]
