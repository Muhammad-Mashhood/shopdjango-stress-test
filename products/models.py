"""
products/models.py - Product catalog models
Depends on: accounts.models
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import force_str
from django.core.validators import MinValueValidator, MaxValueValidator
from jsonfield import JSONField

from accounts.models import UserProfile


class Category(models.Model):
    """Product category with support for subcategories."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subcategories',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_category_name'),
            models.UniqueConstraint(fields=['slug'], name='unique_category_slug'),
        ]

    def __str__(self):
        return force_str(self.name)

    def get_ancestors(self):
        """Return all ancestor categories."""
        ancestors = []
        category = self
        while category.parent:
            ancestors.append(category.parent)
            category = category.parent
        return ancestors


class Brand(models.Model):
    """Product brand."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('brand')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_brand_name'),
            models.UniqueConstraint(fields=['slug'], name='unique_brand_slug'),
        ]

    def __str__(self):
        return force_str(self.name)


class Tag(models.Model):
    """Product tag for filtering."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_tag_name'),
            models.UniqueConstraint(fields=['slug'], name='unique_tag_slug'),
        ]

    def __str__(self):
        return force_str(self.name)


class Product(models.Model):
    """Main product model."""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('archived', _('Archived')),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, null=True, blank=True, related_name='products', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='products')
    created_by = models.ForeignKey(UserProfile, related_name='created_products', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = JSONField(default=dict)  # {length, width, height}
    attributes = JSONField(default=dict)  # Dynamic product attributes
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('product')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['status', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='unique_product_slug'),
            models.UniqueConstraint(fields=['sku'], name='unique_product_sku'),
        ]

    def __str__(self):
        return force_str(self.name)

    def get_discount_percentage(self):
        """Calculate discount percentage if compare_price is set."""
        if self.compare_price and self.compare_price > self.price:
            discount = (self.compare_price - self.price) / self.compare_price * 100
            return round(float(discount), 2)
        return 0

    def is_on_sale(self):
        return self.compare_price is not None and self.compare_price > self.price


class ProductImage(models.Model):
    """Images associated with a product."""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'created_at']

    def __str__(self):
        return force_str('%s - Image %s' % (self.product.name, self.pk))


class ProductVariant(models.Model):
    """Product variant (e.g. size, color combinations)."""
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    attributes = JSONField(default=dict)  # {color: 'red', size: 'XL'}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('product variant')
        constraints = [
            models.UniqueConstraint(fields=['sku'], name='unique_variant_sku'),
        ]

    def __str__(self):
        return force_str('%s - %s' % (self.product.name, self.name))

    def get_price(self):
        """Return variant price, falling back to product price."""
        return self.price if self.price is not None else self.product.price