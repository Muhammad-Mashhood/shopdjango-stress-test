"""
reviews/models.py - Product reviews and ratings
Depends on: accounts.models, products.models, orders.models
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _
from six import python_2_unicode_compatible

from accounts.models import UserProfile
from products.models import Product


@python_2_unicode_compatible
class Review(models.Model):
    """A product review submitted by a customer."""
    product = models.ForeignKey(Product, related_name='reviews')
    user = models.ForeignKey(UserProfile, related_name='reviews')
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
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return u'%s rated %s: %d/5' % (self.user.email, self.product.name, self.rating)


@python_2_unicode_compatible
class ReviewVote(models.Model):
    """Tracks whether a user found a review helpful."""
    review = models.ForeignKey(Review, related_name='votes')
    user = models.ForeignKey(UserProfile, related_name='review_votes')
    is_helpful = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        return u'%s voted on review #%s' % (self.user.email, self.review.pk)


@python_2_unicode_compatible
class Question(models.Model):
    """Customer Q&A for a product."""
    product = models.ForeignKey(Product, related_name='questions')
    user = models.ForeignKey(UserProfile, related_name='questions')
    question = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'Q: %s on %s' % (self.question[:50], self.product.name)


@python_2_unicode_compatible
class Answer(models.Model):
    """Answer to a product question."""
    question = models.ForeignKey(Question, related_name='answers')
    user = models.ForeignKey(UserProfile, related_name='answers')
    answer = models.TextField()
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'A: %s' % self.answer[:50]
