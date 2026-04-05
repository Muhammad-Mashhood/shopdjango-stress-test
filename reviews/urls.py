from django.urls import re_path
from reviews import views

urlpatterns = [
    re_path(r'^product/(?P<product_id>\d+)/$', views.ReviewListCreateView.as_view(), name='review-list'),
    re_path(r'^(?P<review_id>\d+)/approve/$', views.approve_review, name='review-approve'),
    re_path(r'^(?P<review_id>\d+)/vote/$', views.vote_review, name='review-vote'),
    re_path(r'^product/(?P<product_id>\d+)/questions/$', views.QuestionListCreateView.as_view(), name='question-list'),
]
