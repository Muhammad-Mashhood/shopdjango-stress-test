"""
reviews/models.py - Product reviews and ratings
Depends on: accounts.models, products.models, orders.models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import UniqueConstraint, Index

from accounts.models import UserProfile
from products.models import Product


class Review(models.Model):
    """A product review submitted by a customer."""
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='reviews', on_delete=models.CASCADE)
    order_id = models.IntegerField(null=True, blank=True)  # Avoids circular import
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('review')
        constraints = [
            UniqueConstraint(fields=['product', 'user'], name='unique_review')
        ]
        indexes = [
            Index(fields=['-created_at'])
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} rated {self.product.name}: {self.rating}/5'


class ReviewVote(models.Model):
    """Tracks whether a user found a review helpful."""
    review = models.ForeignKey(Review, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='review_votes', on_delete=models.CASCADE)
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['review', 'user'], name='unique_review_vote')
        ]

    def __str__(self):
        return f'{self.user.email} voted on review #{self.review.pk}'


class Question(models.Model):
    """Customer Q&A for a product."""
    product = models.ForeignKey(Product, related_name='questions', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='questions', on_delete=models.CASCADE)
    question = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Q: {self.question[:50]} on {self.product.name}'


class Answer(models.Model):
    """Answer to a product question."""
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='answers', on_delete=models.CASCADE)
    answer = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'A: {self.answer[:50]}'