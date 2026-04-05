from django.urls import re_path
from shipping import views

urlpatterns = [
    re_path(r'^zones/$', views.ShippingZoneListView.as_view(), name='zone-list'),
    re_path(r'^rates/$', views.ShippingRateListView.as_view(), name='rate-list'),
    re_path(r'^shipments/$', views.ShipmentListView.as_view(), name='shipment-list'),
    re_path(r'^shipments/(?P<pk>\d+)/track/$', views.update_tracking, name='shipment-track'),
]
