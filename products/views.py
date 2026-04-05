"""
products/views.py - Product CRUD views
Depends on: products.models, products.serializers, products.filters, products.utils
"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from rest_framework import generics, filters, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from products.models import Category, Brand, Tag, Product, ProductImage, ProductVariant
from products.serializers import (
    CategorySerializer, BrandSerializer, TagSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer
)
from products.filters import ProductFilter
from products.utils import update_product_view_count, get_featured_products
from accounts.utils import log_user_activity


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True, parent=None)
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (permissions.AllowAny,)


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = (permissions.AllowAny,)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'description', 'sku', 'category__name', 'brand__name')
    ordering_fields = ('price', 'created_at', 'average_rating', 'name')
    ordering = ('-created_at',)

    def get_queryset(self):
        queryset = Product.objects.filter(status='active').select_related(
            'category', 'brand'
        ).prefetch_related('images', 'tags')
        # Apply category filter
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        # Apply brand filter
        brand_slug = self.request.query_params.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(status='active')
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        update_product_view_count(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = (permissions.IsAdminUser,)

    def perform_create(self, serializer):
        product = serializer.save(created_by=self.request.user)
        log_user_activity(self.request.user, 'product_created', self.request)


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = (permissions.IsAdminUser,)

    def perform_update(self, serializer):
        serializer.save()
        log_user_activity(self.request.user, 'product_updated', self.request)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def featured_products(request):
    """Return featured products for homepage."""
    products = get_featured_products()
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def related_products(request, product_id):
    """Return products related to a given product."""
    try:
        product = Product.objects.get(pk=product_id, status='active')
        related = Product.objects.filter(
            category=product.category, status='active'
        ).exclude(pk=product_id)[:8]
        serializer = ProductListSerializer(related, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': force_text(_('Product not found'))}, status=status.HTTP_404_NOT_FOUND)
