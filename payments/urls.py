from django.conf.urls import url
from payments import views

urlpatterns = [
    url(r'^intent/$', views.create_payment_intent, name='payment-intent'),
    url(r'^confirm/$', views.confirm_payment, name='payment-confirm'),
    url(r'^refund/$', views.process_refund_view, name='payment-refund'),
    url(r'^history/$', views.PaymentHistoryView.as_view(), name='payment-history'),
]
