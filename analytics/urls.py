from django.conf.urls import url
from analytics import views

urlpatterns = [
    url(r'^track/product/(?P<product_id>\d+)/$', views.track_product_view, name='track-product'),
    url(r'^track/search/$', views.track_search, name='track-search'),
    url(r'^dashboard/$', views.dashboard_summary, name='dashboard'),
    url(r'^reports/$', views.SalesReportListView.as_view(), name='report-list'),
    url(r'^reports/generate/$', views.generate_report, name='report-generate'),
]
