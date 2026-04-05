from django.urls import re_path
from orders import views

urlpatterns = [
    re_path(r'^cart/$', views.CartView.as_view(), name='cart'),
    re_path(r'^cart/add/$', views.add_to_cart, name='cart-add'),
    re_path(r'^cart/remove/(?P<item_id>\d+)/$', views.remove_from_cart, name='cart-remove'),
    re_path(r'^checkout/$', views.checkout, name='checkout'),
    re_path(r'^$', views.OrderListView.as_view(), name='order-list'),
    re_path(r'^(?P<pk>\d+)/$', views.OrderDetailView.as_view(), name='order-detail'),
]
