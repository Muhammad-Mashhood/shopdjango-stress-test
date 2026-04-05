"""
products/admin.py - Admin configuration for products
"""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from products.models import Category, Brand, Tag, Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'sort_order')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('sku', 'name', 'price', 'is_active')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'brand', 'price', 'status', 'featured', 'average_rating')
    list_filter = ('status', 'featured', 'category', 'brand')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    filter_horizontal = ('tags',)
    raw_id_fields = ('category', 'brand', 'created_by')
    readonly_fields = ('view_count', 'average_rating', 'review_count')
    fieldsets = (
        (_('Basic Info'), {'fields': ('name', 'slug', 'sku', 'status', 'featured')}),
        (_('Description'), {'fields': ('description', 'short_description')}),
        (_('Classification'), {'fields': ('category', 'brand', 'tags', 'created_by')}),
        (_('Pricing'), {'fields': ('price', 'compare_price', 'cost_price')}),
        (_('Physical'), {'fields': ('weight', 'dimensions')}),
        (_('Stats'), {'fields': ('view_count', 'average_rating', 'review_count')}),
        (_('Attributes'), {'fields': ('attributes',)}),
    )
