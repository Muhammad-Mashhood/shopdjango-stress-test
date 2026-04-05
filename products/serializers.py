"""
products/serializers.py - DRF serializers for products
Depends on: products.models, accounts.serializers
"""
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from products.models import Category, Brand, Tag, Product, ProductImage, ProductVariant
from accounts.serializers import UserPublicSerializer


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'image',
                  'is_active', 'subcategories', 'product_count')

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data

    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'description', 'logo', 'website', 'is_active')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'sort_order')


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'name', 'price', 'attributes', 'is_active', 'effective_price')

    def get_effective_price(self, obj):
        return float(obj.get_price())


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    primary_image = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'price', 'compare_price',
            'category_name', 'brand_name', 'primary_image', 'status',
            'featured', 'average_rating', 'review_count', 'discount_percentage'
        )

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first()
        if image:
            return ProductImageSerializer(image).data
        return None

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product serializer with all relationships."""
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    created_by = UserPublicSerializer(read_only=True)
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'sku', 'description', 'short_description',
            'category', 'brand', 'tags', 'images', 'variants', 'created_by',
            'price', 'compare_price', 'status', 'featured', 'weight',
            'dimensions', 'attributes', 'average_rating', 'review_count',
            'view_count', 'discount_percentage', 'created_at', 'updated_at'
        )

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()
