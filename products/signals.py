"""
products/signals.py - Signal handlers for products
"""
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver

from products.models import Product, ProductImage, ProductVariant


@receiver(pre_save, sender=Product)
def generate_product_slug(sender, instance, **kwargs):
    """Auto-generate slug from product name if not set."""
    if not instance.slug:
        from django.utils.text import slugify
        instance.slug = slugify(instance.name)


@receiver(post_save, sender=Product)
def notify_inventory_on_product_create(sender, instance, created, **kwargs):
    """Create an inventory record when a new product is created."""
    if created:
        from inventory.models import StockLevel
        StockLevel.objects.get_or_create(
            product=instance,
            defaults={'quantity': 0, 'reorder_threshold': 10}
        )


@receiver(post_save, sender=ProductImage)
def ensure_single_primary_image(sender, instance, **kwargs):
    """Ensure only one image per product is marked as primary."""
    if instance.is_primary:
        ProductImage.objects.filter(
            product=instance.product, is_primary=True
        ).exclude(pk=instance.pk).update(is_primary=False)


@receiver(post_delete, sender=Product)
def cleanup_product_images(sender, instance, **kwargs):
    """Delete image files when a product is deleted."""
    for image in instance.images.all():
        if image.image:
            try:
                image.image.delete(save=False)
            except Exception:
                pass
