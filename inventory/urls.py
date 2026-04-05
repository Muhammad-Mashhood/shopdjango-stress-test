from django.urls import re_path
from inventory import views

urlpatterns = [
    re_path(r'^$', views.StockListView.as_view(), name='stock-list'),
    re_path(r'^(?P<pk>\d+)/$', views.StockDetailView.as_view(), name='stock-detail'),
    re_path(r'^movements/$', views.StockMovementListView.as_view(), name='stock-movements'),
    re_path(r'^add/$', views.add_stock_view, name='stock-add'),
]
