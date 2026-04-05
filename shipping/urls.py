from django.conf.urls import url
from shipping import views

urlpatterns = [
    url(r'^zones/$', views.ShippingZoneListView.as_view(), name='zone-list'),
    url(r'^rates/$', views.ShippingRateListView.as_view(), name='rate-list'),
    url(r'^shipments/$', views.ShipmentListView.as_view(), name='shipment-list'),
    url(r'^shipments/(?P<pk>\d+)/track/$', views.update_tracking, name='shipment-track'),
]
