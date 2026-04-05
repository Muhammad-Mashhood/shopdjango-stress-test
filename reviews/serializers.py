"""
reviews/serializers.py - DRF serializers for reviews
"""
from rest_framework import serializers
from reviews.models import Review, ReviewVote, Question, Answer
from accounts.serializers import UserPublicSerializer


class ReviewSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ('id', 'user', 'rating', 'title', 'body', 'is_verified_purchase',
                  'helpful_votes', 'created_at')
        read_only_fields = ('id', 'user', 'is_verified_purchase', 'helpful_votes', 'created_at')


class AnswerSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    class Meta:
        model = Answer
        fields = ('id', 'user', 'answer', 'is_verified', 'created_at')
        read_only_fields = ('id', 'user', 'is_verified', 'created_at')


class QuestionSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ('id', 'user', 'question', 'answers', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
