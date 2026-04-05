from django.conf.urls import url
from orders import views

urlpatterns = [
    url(r'^cart/$', views.CartView.as_view(), name='cart'),
    url(r'^cart/add/$', views.add_to_cart, name='cart-add'),
    url(r'^cart/remove/(?P<item_id>\d+)/$', views.remove_from_cart, name='cart-remove'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^$', views.OrderListView.as_view(), name='order-list'),
    url(r'^(?P<pk>\d+)/$', views.OrderDetailView.as_view(), name='order-detail'),
]
