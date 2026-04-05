from django.urls import re_path
from notifications import views

urlpatterns = [
    re_path(r'^$', views.NotificationListView.as_view(), name='notification-list'),
    re_path(r'^(?P<pk>\d+)/read/$', views.mark_as_read, name='notification-read'),
    re_path(r'^mark-all-read/$', views.mark_all_read, name='notification-mark-all'),
]
