"""
reviews/signals.py - Signal handlers for reviews
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reviews.models import Review


@receiver(post_save, sender=Review)
def update_rating_on_review_save(sender, instance, **kwargs):
    if instance.is_approved:
        from products.utils import update_product_rating
        update_product_rating(instance.product)


@receiver(post_delete, sender=Review)
def update_rating_on_review_delete(sender, instance, **kwargs):
    from products.utils import update_product_rating
    update_product_rating(instance.product)
