from django.urls import re_path
from analytics import views

urlpatterns = [
    re_path(r'^track/product/(?P<product_id>\d+)/$', views.track_product_view, name='track-product'),
    re_path(r'^track/search/$', views.track_search, name='track-search'),
    re_path(r'^dashboard/$', views.dashboard_summary, name='dashboard'),
    re_path(r'^reports/$', views.SalesReportListView.as_view(), name='report-list'),
    re_path(r'^reports/generate/$', views.generate_report, name='report-generate'),
]
