from django.conf.urls import url
from reviews import views

urlpatterns = [
    url(r'^product/(?P<product_id>\d+)/$', views.ReviewListCreateView.as_view(), name='review-list'),
    url(r'^(?P<review_id>\d+)/approve/$', views.approve_review, name='review-approve'),
    url(r'^(?P<review_id>\d+)/vote/$', views.vote_review, name='review-vote'),
    url(r'^product/(?P<product_id>\d+)/questions/$', views.QuestionListCreateView.as_view(), name='question-list'),
]
