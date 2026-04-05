from django.conf.urls import url
from inventory import views

urlpatterns = [
    url(r'^$', views.StockListView.as_view(), name='stock-list'),
    url(r'^(?P<pk>\d+)/$', views.StockDetailView.as_view(), name='stock-detail'),
    url(r'^movements/$', views.StockMovementListView.as_view(), name='stock-movements'),
    url(r'^add/$', views.add_stock_view, name='stock-add'),
]
