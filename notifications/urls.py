from django.conf.urls import url
from notifications import views

urlpatterns = [
    url(r'^$', views.NotificationListView.as_view(), name='notification-list'),
    url(r'^(?P<pk>\d+)/read/$', views.mark_as_read, name='notification-read'),
    url(r'^mark-all-read/$', views.mark_all_read, name='notification-mark-all'),
]
