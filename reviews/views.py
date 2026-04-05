"""
reviews/views.py - Product review views
Depends on: reviews.models, reviews.serializers, products.utils, notifications.utils
"""
from django.core.urlresolvers import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from reviews.models import Review, ReviewVote, Question, Answer
from reviews.serializers import ReviewSerializer, QuestionSerializer, AnswerSerializer
from products.utils import update_product_rating
from notifications.utils import create_notification


class ReviewListCreateView(generics.ListCreateAPIView):
    """List and create reviews for a product."""
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id, is_approved=True)

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        from products.models import Product
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(force_str(_('Product not found')))

        # Verify purchase - check if user has ordered this product
        from orders.models import OrderItem
        is_verified = OrderItem.objects.filter(
            order__user=self.request.user,
            product=product,
            order__status='delivered'
        ).exists()

        review = serializer.save(
            product=product,
            user=self.request.user,
            is_verified_purchase=is_verified,
            is_approved=False,
        )
        update_product_rating(product)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def approve_review(request, review_id):
    """Approve a review (admin only)."""
    try:
        review = Review.objects.get(pk=review_id)
        review.is_approved = True
        review.save()
        update_product_rating(review.product)
        create_notification(
            review.user, 'review_approved',
            'Review Approved',
            'Your review for "%s" has been approved.' % review.product.name,
            related_object_id=review.pk,
            related_object_type='review'
        )
        return Response({'message': force_str(_('Review approved'))})
    except Review.DoesNotExist:
        return Response({'error': force_str(_('Review not found'))}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def vote_review(request, review_id):
    """Vote a review as helpful or not."""
    is_helpful = request.data.get('is_helpful', True)
    try:
        review = Review.objects.get(pk=review_id, is_approved=True)
        vote, created = ReviewVote.objects.get_or_create(
            review=review,
            user=request.user,
            defaults={'is_helpful': is_helpful}
        )
        if not created:
            vote.is_helpful = is_helpful
            vote.save()

        helpful_count = ReviewVote.objects.filter(review=review, is_helpful=True).count()
        Review.objects.filter(pk=review_id).update(helpful_votes=helpful_count)
        return Response({'helpful_votes': helpful_count})
    except Review.DoesNotExist:
        return Response({'error': force_str(_('Review not found'))}, status=status.HTTP_404_NOT_FOUND)


class QuestionListCreateView(generics.ListCreateAPIView):
    """List and post questions about a product."""
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(product_id=self.kwargs['product_id'], is_active=True)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        from products.models import Product
        product = Product.objects.get(pk=self.kwargs['product_id'])
        serializer.save(product=product, user=self.request.user)
