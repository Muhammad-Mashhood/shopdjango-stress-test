from django.urls import re_path
from payments import views

urlpatterns = [
    re_path(r'^intent/$', views.create_payment_intent, name='payment-intent'),
    re_path(r'^confirm/$', views.confirm_payment, name='payment-confirm'),
    re_path(r'^refund/$', views.process_refund_view, name='payment-refund'),
    re_path(r'^history/$', views.PaymentHistoryView.as_view(), name='payment-history'),
]
