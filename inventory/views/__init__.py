from django_filters import rest_framework as django_filters
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from libs.pagination import CustomPagination
from common.serializers import SetFileSerializer
from ..models import Product, Unit, Category, Warehouse
from ..serializers.product import ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer, ProductEditSerializer
from ..serializers.unit import UnitCreateUpdateSerializer, UnitDetailSerializer, UnitListSerializer
from ..serializers.category import CategoryListSerializer, CategoryDetailSerializer
from ..serializers.warehouse import WarehouseSerializer, WarehouseListSerializer

class ProductFilter(django_filters.FilterSet):
    sku = django_filters.CharFilter(lookup_expr='iexact')
    category = django_filters.NumberFilter(field_name='category__id')
    product_type = django_filters.ChoiceFilter(choices=Product.PRODUCT_TYPE_CHOICES)
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Product
        fields = ['sku', 'category', 'product_type', 'is_active']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    filter_backends = (filters.SearchFilter, django_filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    search_fields = ['name',]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductEditSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['post'], serializer_class=SetFileSerializer)
    def set_picture(self, request, id32=None):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file_instance = serializer.save()

        # Link it to the product
        product.picture = file_instance
        product.save()

        return Response({"message": "Picture set successfully!"}, status=status.HTTP_200_OK)


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return UnitListSerializer
        elif self.action == 'retrieve':
            return UnitDetailSerializer
        return UnitCreateUpdateSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategoryDetailSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    permission_classes = [permissions.IsAuthenticated,
                          permissions.DjangoModelPermissions]
    lookup_field = 'id32'
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter, django_filters.DjangoFilterBackend]
    search_fields = ['name', 'address']
    filterset_fields = ['type']

    def get_serializer_class(self):
        if self.action == 'list':
            return WarehouseListSerializer
        return WarehouseSerializer
